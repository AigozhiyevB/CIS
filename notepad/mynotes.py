from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys
import uuid

IMAGE_EXTENSIONS = ['.jpg','.png','.bmp']

def splitext(p):
    return os.path.splitext(p)[1].lower()


class TextEdit(QTextEdit):

    def canInsertFromMimeData(self, source):

        if source.hasImage():
            return True
        else:
            return super(TextEdit, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        print("Me")

        cursor = self.textCursor()
        document = self.document()

        if source.hasUrls():

            for u in source.urls():
                file_ext = splitext(str(u.toLocalFile()))
                if u.isLocalFile() and file_ext in IMAGE_EXTENSIONS:
                    image = QImage(u.toLocalFile())
                    document.addResource(QTextDocument.ImageResource, u, image)
                    cursor.insertImage(u.toLocalFile())

                else:
                    # Если не изоражение - break
                    break

            else:
                # Если все изображения валидны, заканчиваем здесь
                return


        elif source.hasImage():
            image = source.imageData()
            uuid = hexuuid()
            document.addResource(QTextDocument.ImageResource, uuid, image)
            cursor.insertImage(uuid)
            return

        super(TextEdit, self).insertFromMimeData(source)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.editor = TextEdit() #Пользовательский класс

        # Начальные позиция и размер окна
        self.left = 100
        self.top = 100
        self.width = 640
        self.heigh = 480

        self.setGeometry(self.left, self.top, self.width, self.heigh)

        # Настраиваем QTextEditor
        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(12)
        self.editor.setFont(fixedfont)

        # self.path зранит путь открытого окна
        # None, если мы еще не отрыли файл или создаем новый
        self.path = None

        layout.addWidget(self.editor)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        file_toolbar = QToolBar("file")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&Файл")

        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Открыть файл...", self)
        open_file_action.setStatusTip("Открыть файл")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join('images', 'disk.png')), "Сохранить", self)
        save_file_action.setStatusTip("Сохранить текущую страницу")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        saveas_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Сохранить как...", self)
        saveas_file_action.setStatusTip("Сохранить текущую страницу как новый файл")
        saveas_file_action.triggered.connect(self.file_save_as)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)

        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Печать...", self)
        print_action.setStatusTip("Печать текущей страницы")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Изменить")

        undo_action = QAction(QIcon(os.path.join('images', 'arrow-curve-180-left.png')), "Убрать", self)
        undo_action.setStatusTip("Убирает последние изменения")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Вернуть", self)
        redo_action.setStatusTip("Возвращает последние изменения")
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Вырезать", self)
        cut_action.setStatusTip("Вырезать выделенный текст")
        cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Копировать", self)
        copy_action.setStatusTip("Скопировать выделенный текст")
        copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Вставить", self)
        paste_action.setStatusTip("Вставить из буфера обмена")
        cut_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(QIcon(os.path.join('images', 'selection-input.png')), "Выделить все", self)
        select_action.setStatusTip("Выделить весь текст")
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)


        self.update_title()
        self.show()

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Text documents (*.txt);All files (*.*)")

        if path:
            try:
                with open(path, 'rU') as f:
                    text = f.read()

            except Exception as e:
                self.dialog_critical(str(e))

            else:
                self.path = path
                self.editor.setPlainText(text)
                self.update_title()

    def file_save(self):
        if self.path is None:
            # Если у файла нет пути, заускаем "Сохранить как"
            return self.file_save_as()

        self._save_to_path(self.path)

    def file_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Текстовые документы (*.txt);Все файлы (*.*)")

        if not path:
            # Если окно диалога было закрыто, возвращаем ''
            return

        self._save_to_path(path)

    def _save_to_path(self, path):
        text = self.editor.toPlainText()
        try:
            with open(path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())

    def update_title(self):
        self.setWindowTitle("%s - Заметки" % (os.path.basename(self.path) if self.path else "Безымянный"))

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode( 1 if self.editor.lineWrapMode() == 0 else 0 )


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName("MyNotes")

    window = MainWindow()
    app.exec_()