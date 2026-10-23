"""Session-only PNG branding with a local still-frame placement preview."""
from pathlib import Path
from PySide6.QtCore import Qt, QRectF, QProcess, QTimer, QSize
from PySide6.QtGui import QImage, QPainter, QColor, QPen
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QComboBox, QFileDialog, QMessageBox, QDialogButtonBox)


def logo_rect(frame, image, width, x, y):
    size = min(frame.width()*width, frame.height()*.8*image.width()/image.height())
    height = size*image.height()/image.width()
    return QRectF(frame.x()+(frame.width()-size)*x, frame.y()+(frame.height()-height)*y, size, height)


class Canvas(QWidget):
    def __init__(self):
        super().__init__(); self.setMinimumSize(420,230)
        self.frame=QImage();self.logo=QImage();self.width_fraction=.15;self.opacity=.7;self.x=.95;self.y=.95;self.drag=None
    def frame_rect(self):
        size=self.frame.size() if not self.frame.isNull() else QSize(1600,900)
        size.scale(self.size(),Qt.KeepAspectRatio)
        return QRectF((self.width()-size.width())/2,(self.height()-size.height())/2,size.width(),size.height())
    def overlay_rect(self):return logo_rect(self.frame_rect(),self.logo,self.width_fraction,self.x,self.y)
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('#111318'));frame=self.frame_rect();p.fillRect(frame,Qt.black)
        if not self.frame.isNull():p.drawImage(frame,self.frame)
        if not self.logo.isNull():
            rect=self.overlay_rect();p.setOpacity(self.opacity);p.drawImage(rect,self.logo);p.setOpacity(1);p.setPen(QPen(QColor('#57d5ed'),1));p.drawRect(rect)
    def mousePressEvent(self,event):
        if not self.logo.isNull() and event.button()==Qt.LeftButton and self.overlay_rect().contains(event.position()):
            self.drag=event.position()-self.overlay_rect().topLeft();self.setCursor(Qt.ClosedHandCursor)
    def mouseMoveEvent(self,event):
        if self.drag is None:return
        frame=self.frame_rect();rect=self.overlay_rect();pos=event.position()-self.drag
        self.x=max(0,min(1,(pos.x()-frame.x())/max(1,frame.width()-rect.width())))
        self.y=max(0,min(1,(pos.y()-frame.y())/max(1,frame.height()-rect.height())))
        self.update()
    def mouseReleaseEvent(self,event):self.drag=None;self.unsetCursor()


class WatermarkDialog(QDialog):
    def __init__(self,source,config,parent=None):
        super().__init__(parent);self.setWindowTitle('الشعار والعلامة المائية');self.resize(760,590)
        self.source=source;self.path=config.get('file');self.canvas=Canvas();self.preview=None
        self.canvas.x=config.get('x',.95);self.canvas.y=config.get('y',.95)
        box=QVBoxLayout(self);box.addWidget(QLabel('اختر صورة PNG ثم اسحب الشعار داخل الفيديو لتحديد مكانه.'))
        line=QHBoxLayout();button=QPushButton('اختيار شعار PNG…');button.clicked.connect(self.choose);line.addWidget(button)
        self.filename=QLabel(Path(self.path).name if self.path else 'بدون شعار');line.addWidget(self.filename,1);box.addLayout(line)
        box.addWidget(self.canvas,1)
        self.note=QLabel('جارٍ تجهيز لقطة المعاينة…' if source else 'اختر فيديو في النافذة الرئيسية لمعاينة الخلفية.');self.note.setWordWrap(True);box.addWidget(self.note)
        line=QHBoxLayout();self.position=QComboBox();self.position.addItems(['مكان حر / بالسحب','أعلى اليسار','أعلى اليمين','أسفل اليسار','أسفل اليمين','المنتصف'])
        self.position.currentIndexChanged.connect(self.place);line.addWidget(QLabel('المكان'));line.addWidget(self.position);box.addLayout(line)
        self.size_label=QLabel();self.size=QSlider(Qt.Horizontal);self.size.setRange(5,40);self.size.setValue(round(config.get('width',.15)*100))
        self.opacity_label=QLabel();self.opacity=QSlider(Qt.Horizontal);self.opacity.setRange(0,100);self.opacity.setValue(round(config.get('opacity',.7)*100))
        for label,slider in [(self.size_label,self.size),(self.opacity_label,self.opacity)]:
            row=QHBoxLayout();row.addWidget(label);row.addWidget(slider,1);box.addLayout(row);slider.valueChanged.connect(self.refresh)
        box.addWidget(QLabel('معاينة ثابتة. يُطبّق الشعار على الفيديو كله عند التصدير، وقد يزيد وقت المعالجة.'))
        buttons=QDialogButtonBox();self.apply=buttons.addButton('تطبيق',QDialogButtonBox.AcceptRole);buttons.addButton('إلغاء',QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);box.addWidget(buttons)
        self.apply.setEnabled(False)
        if self.path:self.set_logo(self.path)
        self.refresh()
        if source:QTimer.singleShot(0,self.load_frame)
    def choose(self):
        path,_=QFileDialog.getOpenFileName(self,'اختيار شعار','','PNG (*.png)')
        if path:self.set_logo(path)
    def set_logo(self,path):
        try:
            file=Path(path)
            if file.stat().st_size>20*1024*1024 or file.read_bytes()[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError()
            image=QImage(str(file))
            if image.isNull() or not 0<image.width()<=8192 or not 0<image.height()<=8192:raise ValueError()
        except (OSError,ValueError):
            QMessageBox.warning(self,'الشعار','اختر صورة PNG صالحة لا تتجاوز 20 ميجابايت و8192 بكسل لكل بُعد.');return
        self.path=str(file.resolve());self.canvas.logo=image;self.filename.setText(file.name);self.apply.setEnabled(True);self.canvas.update()
    def refresh(self):
        self.canvas.width_fraction=self.size.value()/100;self.canvas.opacity=self.opacity.value()/100
        self.size_label.setText(f'الحجم: {self.size.value()}٪ من عرض الفيديو');self.opacity_label.setText(f'العتامة: {self.opacity.value()}٪');self.canvas.update()
    def place(self,index):
        positions=[None,(.05,.05),(.95,.05),(.05,.95),(.95,.95),(.5,.5)]
        if positions[index]:self.canvas.x,self.canvas.y=positions[index];self.canvas.update()
    def load_frame(self):
        self.preview=QProcess(self);self.preview.finished.connect(self.frame_ready)
        self.preview.errorOccurred.connect(lambda *_:self.note.setText('تعذرت معاينة الخلفية. ثبّت أدوات المعالجة؛ يمكنك تحديد مكان الشعار على الإطار.'))
        self.preview.start('ffmpeg',['-nostdin','-v','error','-i',str(self.source),'-frames:v','1','-vf','scale=960:-2','-f','image2pipe','-vcodec','png','pipe:1'])
        QTimer.singleShot(15000,self.timeout)
    def timeout(self):
        if self.preview and self.preview.state()!=QProcess.NotRunning:self.preview.kill()
    def frame_ready(self,*args):
        image=QImage.fromData(bytes(self.preview.readAllStandardOutput()),'PNG')
        if not image.isNull():self.canvas.frame=image;self.note.setText('اسحب الشعار لتغيير مكانه. نسبة أبعاد الإطار مطابقة للفيديو.');self.canvas.update()
        else:self.note.setText('تعذرت معاينة الخلفية. ثبّت أدوات المعالجة أو جرّب فيديو آخر.')
    def result_config(self):
        return dict(file=self.path,width=self.canvas.width_fraction,x=self.canvas.x,y=self.canvas.y,opacity=self.canvas.opacity)
    def done(self,result):
        if self.preview and self.preview.state()!=QProcess.NotRunning:self.preview.kill();self.preview.waitForFinished(1000)
        super().done(result)
