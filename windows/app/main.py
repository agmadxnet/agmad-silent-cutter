"""Agmad Silent Cutter: Arabic Windows desktop interface."""
import json
import os
from pathlib import Path
import sys
import tempfile
from PySide6.QtCore import Qt, QProcess, QProcessEnvironment, QSettings, QTimer, QUrl, QStandardPaths, QLockFile
from PySide6.QtGui import QIcon, QDesktopServices, QCloseEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QFileDialog, QSlider, QCheckBox, QProgressBar,
    QMessageBox, QLineEdit, QButtonGroup, QDoubleSpinBox)
from paths import ROOT, DATA, prepare
from tools.cut_settings import resolve, LIMITS
from tools.process import PRESETS


def mapped_time(milliseconds, clips):
    seconds = milliseconds / 1000
    clip = next((c for c in reversed(clips) if seconds >= c['start']), clips[0] if clips else None)
    if not clip: return 0
    return round((clip['source'] + min(max(0, seconds-clip['start']), clip['duration']))*1000)


class Player(QWidget):
    def __init__(self, heading):
        super().__init__()
        box=QVBoxLayout(self); box.addWidget(QLabel(heading))
        self.video=QVideoWidget(); self.video.setMinimumSize(240,140); box.addWidget(self.video,1)
        self.media=QMediaPlayer(self); self.sound=QAudioOutput(self); self.media.setAudioOutput(self.sound); self.media.setVideoOutput(self.video)
        controls=QHBoxLayout(); self.play=QPushButton('تشغيل / إيقاف'); self.slider=QSlider(Qt.Horizontal); self.time=QLabel('00:00')
        controls.addWidget(self.play); controls.addWidget(self.slider,1); controls.addWidget(self.time); box.addLayout(controls)
        self.play.clicked.connect(self.toggle); self.slider.sliderMoved.connect(self.media.setPosition)
        self.media.durationChanged.connect(lambda d:self.slider.setRange(0,d))
        self.media.positionChanged.connect(self.position)
    def toggle(self):
        if self.media.playbackState()==QMediaPlayer.PlayingState:self.media.pause()
        else:self.media.play()
    def position(self,value):
        if not self.slider.isSliderDown():self.slider.setValue(value)
        self.time.setText(f'{value//60000:02d}:{(value//1000)%60:02d}')
    def controls(self,enabled):self.play.setEnabled(enabled);self.slider.setEnabled(enabled)


class Window(QMainWindow):
    def __init__(self):
        super().__init__(); prepare(); self.setWindowTitle('Agmad Silent Cutter'); self.setWindowIcon(QIcon(str(ROOT/'assets/icon.ico')))
        screen=QApplication.primaryScreen().availableGeometry();self.resize(min(1160,screen.width()-40),min(780,screen.height()-60)); self.setMinimumSize(900,700); self.setAcceptDrops(True)
        self.settings=QSettings('Agmad','SilentCutterWindows'); self.source=None;self.output=None;self.log=None;self.clips=[]
        self.worker=None;self.cancel_path=None;self.buffer=b'';self.done=False;self.pending_close=False;self.cancelling=False
        central=QWidget();self.setCentralWidget(central);layout=QVBoxLayout(central);layout.setContentsMargins(20,16,20,16);layout.setSpacing(7)
        brand=QLabel('A G M A D   /   LOCAL VIDEO TOOLS                                      1.4.0');brand.setObjectName('Brand');layout.addWidget(brand)
        title=QLabel('Agmad Silent Cutter');title.setObjectName('Title');layout.addWidget(title)
        layout.addWidget(QLabel('تنظيف الصوت وقص فترات الصمت محليًا — مع الحفاظ على الملفات الأصلية'))
        self.choose=QPushButton('اختيار فيديو…');self.file=QLineEdit('اختر فيديو أو اسحبه إلى النافذة');self.file.setReadOnly(True)
        line=QHBoxLayout();line.addWidget(self.choose);line.addWidget(self.file,1);layout.addLayout(line);self.choose.clicked.connect(self.select_file)
        self.folder_button=QPushButton('مكان حفظ النتائج…');self.folder=QLineEdit();self.folder.setReadOnly(True)
        videos=QStandardPaths.writableLocation(QStandardPaths.MoviesLocation)
        self.destination=Path(self.settings.value('destination',str(Path(videos)/'Agmad Silent Cutter')))
        self.folder.setText(str(self.destination));line=QHBoxLayout();line.addWidget(self.folder_button);line.addWidget(self.folder,1);layout.addLayout(line)
        self.folder_button.clicked.connect(self.select_folder)
        self.custom_values=[float(self.settings.value(k,d)) for k,d in [('customThreshold',2),('customPadding',.3),('customPause',.8)]]
        line=QHBoxLayout();self.profile=QComboBox();self.profile.addItems(['مقياس القص','مخصص']);line.addWidget(self.profile)
        self.levels=QButtonGroup(self);self.level_buttons=[]
        for index,number in enumerate(range(-5,6)):
            b=QPushButton(f'{number:+d}' if number else '0');b.setCheckable(True);b.setFixedWidth(40);self.levels.addButton(b,index);line.addWidget(b);self.level_buttons.append(b)
        saved=int(self.settings.value('scaleLevel',self.settings.value('level',0)))
        self.levels.button(min(5,max(-5,saved))+5).setChecked(True)
        self.advanced=QCheckBox('الإعدادات المتقدمة');line.addWidget(self.advanced);line.addStretch();layout.addLayout(line)
        self.custom_panel=QWidget();custom_line=QHBoxLayout(self.custom_panel);custom_line.setContentsMargins(0,0,0,0);self.fields=[]
        for label,key in [('عتبة الصوت %','threshold'),('هامش الكلام / ثانية','padding'),('أقل صمت / ثانية','pause')]:
            custom_line.addWidget(QLabel(label));field=QDoubleSpinBox();field.setDecimals(3);field.setRange(*LIMITS[key]);field.setSingleStep(.5 if key=='threshold' else .025);custom_line.addWidget(field);self.fields.append(field)
        self.reset_custom=QPushButton('نسخ مستوى المقياس');custom_line.addWidget(self.reset_custom);layout.addWidget(self.custom_panel)
        self.profile.setCurrentIndex(min(1,max(0,int(self.settings.value('cutProfile',0)))))
        self.last_profile=self.profile.currentIndex()
        self.profile.currentIndexChanged.connect(self.profile_changed);self.levels.idClicked.connect(self.refresh_cut_controls)
        self.advanced.toggled.connect(self.custom_panel.setVisible);self.reset_custom.clicked.connect(self.copy_scale)
        self.refresh_cut_controls();self.advanced.setChecked(self.profile.currentIndex()==1);self.custom_panel.setVisible(self.advanced.isChecked())
        line=QHBoxLayout()
        self.mode=QComboBox();self.mode.addItems(['بدون تنظيف','إزالة الضوضاء','إزالة الموسيقى']);self.mode.setCurrentIndex(min(2,max(0,int(self.settings.value('mode',0)))))
        line.addWidget(QLabel('الصوت'));line.addWidget(self.mode)
        self.scope=QComboBox();self.scope.addItems(['الفيديو بالكامل','اختبار 30 ثانية','اختبار 60 ثانية']);line.addWidget(self.scope)
        self.start=QSpinBox();self.start.setRange(0,86400*7);self.start.setEnabled(False);line.addWidget(QLabel('البداية بالثواني'));line.addWidget(self.start)
        self.scope.currentIndexChanged.connect(lambda i:self.start.setEnabled(i>0 and not self.worker));layout.addLayout(line)
        layout.addWidget(QLabel('−5 ألطف قص • 0 متوازن • +1 إلى +5 نفس المستويات السابقة • القيم الأعلى قد تحذف الكلام الهادئ'))
        players=QHBoxLayout();self.before=Player('قبل التعديل — الأصل');self.after=Player('بعد التعديل');players.addWidget(self.before,1);players.addWidget(self.after,1);layout.addLayout(players,1)
        line=QHBoxLayout();self.link=QCheckBox('ربط المقارنة بالفيديو المعدّل');self.link.setChecked(True);self.link.toggled.connect(self.link_changed);line.addWidget(self.link)
        self.audio=QComboBox();self.audio.addItems(['صوت الأصل','الصوت المعدّل']);self.audio.setCurrentIndex(1);self.audio.currentIndexChanged.connect(self.audio_changed);line.addWidget(self.audio);line.addStretch();layout.addLayout(line)
        self.stats=QLabel('الملف الأصلي لن يتغير. جرّب جزءًا قصيرًا أولًا.');layout.addWidget(self.stats)
        line=QHBoxLayout();self.run_button=QPushButton('معالجة الفيديو');self.run_button.setObjectName('Primary')
        self.cancel_button=QPushButton('إلغاء');self.open_button=QPushButton('فتح النتائج');self.report_button=QPushButton('فتح السجل')
        for b in [self.run_button,self.cancel_button,self.open_button,self.report_button]:line.addWidget(b)
        line.addStretch();layout.addLayout(line)
        self.run_button.clicked.connect(self.process);self.cancel_button.clicked.connect(self.cancel);self.open_button.clicked.connect(self.open_output);self.report_button.clicked.connect(self.open_log)
        self.progress=QProgressBar();self.progress.setRange(0,0);self.progress.setMaximumHeight(8);self.progress.hide();layout.addWidget(self.progress)
        self.status=QLabel('جاهز. ثبّت أدوات المعالجة مرة واحدة إذا كانت هذه أول مرة.');self.status.setWordWrap(True);layout.addWidget(self.status)
        line=QHBoxLayout();self.core=QPushButton('تثبيت أدوات المعالجة');self.music=QPushButton('تثبيت تنظيف الموسيقى — اختياري');line.addWidget(self.core);line.addWidget(self.music);line.addStretch();layout.addLayout(line)
        self.core.clicked.connect(lambda:self.setup('core'));self.music.clicked.connect(lambda:self.setup('music'))
        self.timer=QTimer(self);self.timer.setInterval(80);self.timer.timeout.connect(self.follow);self.timer.start()
        self.before.media.errorOccurred.connect(lambda *a:self.media_error(self.before))
        self.after.media.errorOccurred.connect(lambda *a:self.media_error(self.after))
        self.before.controls(False);self.after.controls(False);self.run_button.setEnabled(False);self.cancel_button.setEnabled(False);self.report_button.setEnabled(False);self.audio.setEnabled(False);self.link.setEnabled(False)
    def scale_values(self):
        t,m,s,_=resolve('scale',PRESETS,level=self.levels.checkedId()-5)
        return [float(t.rstrip('%')),float(m.rstrip('s')),float(s.split(',')[0].rstrip('s'))]
    def remember_custom(self):
        self.custom_values=[f.value() for f in self.fields]
    def refresh_cut_controls(self,*args):
        custom=self.profile.currentIndex()==1;values=self.custom_values if custom else self.scale_values()
        for field,key,value in zip(self.fields,['threshold','padding','pause'],values):
            low,high=LIMITS[key];field.setRange(low if custom else min(low,value),high);field.setValue(value);field.setReadOnly(not custom);field.setEnabled(not self.worker)
        self.reset_custom.setEnabled(custom and not self.worker)
        for button in self.level_buttons:button.setEnabled(not custom and not self.worker)
    def profile_changed(self,index):
        if self.last_profile==1:self.remember_custom()
        self.last_profile=index
        if index==1:self.advanced.setChecked(True)
        self.refresh_cut_controls()
    def copy_scale(self):
        self.custom_values=[max(LIMITS[k][0],min(LIMITS[k][1],v)) for k,v in zip(['threshold','padding','pause'],self.scale_values())]
        self.refresh_cut_controls()
    def save_cut_settings(self):
        if self.profile.currentIndex()==1:self.remember_custom()
        self.settings.setValue('scaleLevel',self.levels.checkedId()-5);self.settings.setValue('cutProfile',self.profile.currentIndex())
        for key,value in zip(['customThreshold','customPadding','customPause'],self.custom_values):self.settings.setValue(key,value)
    def select_file(self):
        filename,_=QFileDialog.getOpenFileName(self,'اختيار فيديو','','Video (*.mp4 *.mov *.mkv *.avi *.webm *.m4v)')
        if filename:self.load_file(Path(filename))
    def load_file(self,path):
        if self.worker:return
        self.before.media.stop();self.after.media.stop();self.source=path;self.output=None;self.clips=[]
        self.before.media.setSource(QUrl.fromLocalFile(str(path)));self.after.media.setSource(QUrl())
        self.file.setText(str(path));self.run_button.setEnabled(True);self.before.controls(True);self.after.controls(False);self.audio.setEnabled(False);self.link.setEnabled(False)
        self.before.sound.setMuted(False);self.status.setText('جاهز للمعالجة.')
    def select_folder(self):
        folder=QFileDialog.getExistingDirectory(self,'مكان حفظ النتائج',str(self.destination))
        if folder:self.destination=Path(folder);self.folder.setText(folder);self.settings.setValue('destination',folder)
    def audio_changed(self,*args):
        self.before.sound.setMuted(self.audio.currentIndex()!=0);self.after.sound.setMuted(self.audio.currentIndex()!=1)
    def link_changed(self,*args):
        self.before.media.pause();self.after.media.pause();self.before.controls(not self.link.isChecked() and self.source is not None)
    def follow(self):
        if not self.output or not self.link.isChecked() or not self.clips:return
        target=mapped_time(self.after.media.position(),self.clips)
        if abs(self.before.media.position()-target)>160:self.before.media.setPosition(target)
        playing=self.after.media.playbackState()==QMediaPlayer.PlayingState
        if playing and self.before.media.playbackState()!=QMediaPlayer.PlayingState:self.before.media.play()
        elif not playing and self.before.media.playbackState()==QMediaPlayer.PlayingState:self.before.media.pause()
    def media_error(self,player):
        if player.media.error()!=QMediaPlayer.NoError:self.status.setText('تعذر تشغيل المعاينة: '+player.media.errorString()+' — يمكنك فتح الملف في مشغّل خارجي.')
    def busy(self,value):
        for b in [self.choose,self.folder_button,self.mode,self.scope,self.core,self.music,self.profile,self.advanced,self.reset_custom,*self.fields,*self.level_buttons]:b.setEnabled(not value)
        self.start.setEnabled(not value and self.scope.currentIndex()>0);self.run_button.setEnabled(not value and self.source is not None)
        self.cancel_button.setEnabled(value);self.progress.setVisible(value)
        if not value:self.refresh_cut_controls()
    def start_job(self,script,args):
        self.before.media.pause();self.after.media.pause();self.done=False;self.cancelling=False;self.buffer=b''
        fd,name=tempfile.mkstemp(prefix='cancel_',dir=DATA);os.close(fd);os.unlink(name);self.cancel_path=Path(name)
        self.worker=QProcess(self);self.worker.setProcessChannelMode(QProcess.MergedChannels)
        env=QProcessEnvironment.systemEnvironment();env.insert('AGMAD_CANCEL_FILE',name);env.insert('PYTHONUNBUFFERED','1');env.insert('PYTHONUTF8','1');self.worker.setProcessEnvironment(env)
        self.worker.readyReadStandardOutput.connect(self.read_events);self.worker.finished.connect(self.finished);self.worker.errorOccurred.connect(self.process_error)
        self.busy(True);self.worker.start(sys.executable,['-u',str(script),*args])
    def process(self):
        if not self.source or self.worker:return
        try:self.destination.mkdir(parents=True,exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(self,'مكان الحفظ','تعذر الكتابة في المجلد. اختر مكانًا آخر.\n'+str(exc));return
        self.save_cut_settings();self.settings.setValue('mode',self.mode.currentIndex())
        self.output=None;self.clips=[];self.after.media.setSource(QUrl());self.after.controls(False)
        self.start_job(ROOT/'app/tools/gui_process.py',['--input',str(self.source),'--destination',str(self.destination),'--engine',str(DATA),'--profile',['scale','custom'][self.profile.currentIndex()],'--level',str(self.levels.checkedId()-5),'--threshold',str(self.custom_values[0]),'--padding',str(self.custom_values[1]),'--pause',str(self.custom_values[2]),'--mode',['off','noise','music'][self.mode.currentIndex()],'--start',str(self.start.value()),'--length',str([0,30,60][self.scope.currentIndex()])])
    def setup(self,which):
        if self.worker:return
        message='سيتم تنزيل أدوات المعالجة من الإنترنت مرة واحدة.' if which=='core' else 'تنظيف الموسيقى اختياري. سيُنزل مكتبات ونموذجًا كبيرًا وقد يحتاج عدة جيجابايت. أغلق البرامج الأخرى أثناء استخدامه على جهاز بذاكرة 8GB.'
        self.status.setText(message);self.start_job(ROOT/'app/bootstrap.py',[which])
    def read_events(self):
        if not self.worker:return
        self.buffer+=bytes(self.worker.readAllStandardOutput())
        while b'\n' in self.buffer:
            line,self.buffer=self.buffer.split(b'\n',1)
            try:self.handle_event(json.loads(line))
            except (ValueError,TypeError):pass
    def handle_event(self,e):
        kind=e.get('event')
        if kind=='stage':
            message=e.get('message','')
            translations={'Preparing test excerpt…':'تجهيز الجزء التجريبي…','Preparing local audio cleanup…':'تجهيز تنظيف الصوت…','Removing noise locally...':'إزالة الضوضاء محليًا…','Separating voice from music locally (this can take time)...':'فصل الكلام عن الموسيقى محليًا…','Using cached cleaned audio.':'استخدام الصوت المنظّف المحفوظ لتوفير الوقت.','Finding pauses and building comparison timeline…':'اكتشاف فترات الصمت وتجهيز المقارنة…','Rendering the edited video…':'حفظ الفيديو المعدّل…'}
            self.status.setText(translations.get(message,message))
        elif kind=='log':self.log=Path(e['path']);self.report_button.setEnabled(True)
        elif kind=='error':self.status.setText('حدث خطأ: '+e.get('message','')+' — راجع السجل.');self.done=False
        elif kind=='ready':self.done=True;self.status.setText(e.get('message','اكتمل التثبيت.'))
        elif kind=='cancelled':self.status.setText('تم الإلغاء. الملف الأصلي محفوظ.')
        elif kind=='done':
            self.done=True;self.output=Path(e['output']);self.clips=e['clips'];self.after.media.setSource(QUrl.fromLocalFile(str(self.output)))
            self.after.controls(True);self.audio.setEnabled(True);self.link.setEnabled(True);self.link.setChecked(True);self.before.controls(False);self.audio_changed()
            self.stats.setText(f"الأصل / الجزء: {e['inputDuration']:.1f} ثانية    بعد التعديل: {e['outputDuration']:.1f} ثانية    المحذوف: {e['removedPercent']:.1f}%")
            self.status.setText('اكتملت المعالجة. استخدم مشغّل الفيديو المعدّل للمقارنة المرتبطة.');QApplication.alert(self)
    def process_error(self,error):
        if error==QProcess.FailedToStart:self.status.setText('تعذر بدء المعالجة. أعد استخراج الحزمة كاملة.');self.worker=None;self.busy(False)
    def finished(self,code,*args):
        self.read_events();self.worker.deleteLater();self.worker=None;self.busy(False)
        if self.cancel_path:self.cancel_path.unlink(missing_ok=True)
        if self.cancelling:self.status.setText('تم الإلغاء. الملف الأصلي لم يتغير.')
        elif not self.done and code==0:self.status.setText('انتهت العملية دون نتيجة. راجع السجل.')
        if self.pending_close:self.close()
    def cancel(self):
        if self.worker and self.cancel_path:self.cancelling=True;self.cancel_path.touch();self.cancel_button.setEnabled(False);self.status.setText('جارٍ الإلغاء…')
    def open_output(self):QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.output.parent if self.output else self.destination)))
    def open_log(self):
        if self.log:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.log)))
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls() and not self.worker:event.acceptProposedAction()
    def dropEvent(self,event):
        path=Path(event.mimeData().urls()[0].toLocalFile())
        if path.is_file() and path.suffix.lower() in {'.mp4','.mov','.mkv','.avi','.webm','.m4v'}:self.load_file(path)
    def closeEvent(self,event:QCloseEvent):
        if self.worker:
            if QMessageBox.question(self,'عملية قيد التشغيل','إلغاء العملية وإغلاق البرنامج؟',QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:self.pending_close=True;self.cancel()
            event.ignore()
        else:self.save_cut_settings();self.before.media.stop();self.after.media.stop();event.accept()


if __name__=='__main__':
    app=QApplication(sys.argv);app.setApplicationName('Agmad Silent Cutter');app.setOrganizationName('Agmad');app.setWindowIcon(QIcon(str(ROOT/'assets/icon.ico')))
    app.setStyle('Fusion');app.setStyleSheet((ROOT/'assets/theme.qss').read_text(encoding='utf-8'))
    prepare();lock=QLockFile(str(DATA/'app.lock'))
    if not lock.tryLock(0):QMessageBox.information(None,'Agmad Silent Cutter','البرنامج مفتوح بالفعل.');sys.exit(0)
    window=Window();window.show()
    sys.exit(app.exec())
