#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide2.QtWidgets import (
    QWidget,
    QTableView,
    QHBoxLayout,
    QApplication,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QVBoxLayout,
    QHeaderView,
)
from PySide2.QtCore import (
    QAbstractTableModel,
    Signal,
    Slot,
)
from PySide2.QtGui import QFont, Qt
import json
import sys


class MyTableController:
    def __init__(self, model) -> None:
        super().__init__()
        self.model = model

    @Slot(str)
    def line_remove_change(self, value):
        self.model.line_remove = value

    @Slot(list)
    def change_table(self, lst):
        self.model.data_list = lst

    @Slot(str)
    def line_add_change(self, value):
        self.model.line_add = value

    def remove(self):
        idx = self.model.line_remove
        lst = self.model.data_list
        for i, v in enumerate(lst[1]):
            if f"{idx}" == v[0]:
                lst[1].pop(i)
        self.change_table(lst)

    def save(self):
        with open("table.json", "w", encoding="utf-8") as file:
            json.dump(
                [
                    {
                        "headers": self.model.data_list[0],
                        "table_value": self.model.data_list[1],
                    }
                ],
                file,
                ensure_ascii=False,
            )

    def adding(self):
        line = self.model.line_add
        lst = self.model.data_list
        p = 0
        for i, v in enumerate(lst[1]):
            p = int(v[0])
        line = str(p + 1) + "," + line
        line = line.split(",")
        line[0] = f"{line[0]}"
        line[2] = f"{line[2]}"
        lst[1].append(line)
        self.change_table(lst)


class MyTableModel(QAbstractTableModel):
    list_changed = Signal(list)
    line_remove_change = Signal(str)
    line_add_change = Signal(str)
    editCompleted = Signal(str)

    def __init__(self, parent, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        with open("table.json", "r", encoding="utf-8") as file:
            data = json.load(file)[0]
        date_lst = []
        for i in data["table_value"]:
            date_lst.insert(int(i[0]), i)
        self.__headers, self.__list = data["headers"], date_lst
        self.__data_list = [self.__headers, self.__list]
        self.__line_remove = ""
        self.__line_add = ""

    def rowCount(self, parent):
        return len(self.__list)

    def columnCount(self, parent):
        return len(self.__list[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.EditRole:
            return self.__list[index.row()][index.column()]
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            return self.__list[row][column]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.__headers[col]
        return None

    @property
    def data_list(self):
        return self.__data_list

    @data_list.setter
    def data_list(self, lst):
        self.__data_list = lst
        self.list_changed.emit(lst)


    @property
    def line_remove(self):
        self.reset_model()
        return self.__line_remove

    @line_remove.setter
    def line_remove(self, value):
        self.__line_remove = value

    @property
    def line_add(self):
        self.reset_model()
        return self.__line_add

    @line_add.setter
    def line_add(self, value):
        self.__line_add = value
        self.line_add_change.emit(value)

    def reset_model(self):
        self.beginResetModel()
        self.endResetModel()


class MyTableView:
    def __init__(self, parent, table_model, controller):
        self.parent = parent
        self.table_model = table_model
        self.controller = controller
        self.SetupUI()
        self.btn_del.clicked.connect(self.dels)
        self.btn_add.clicked.connect(self.controller.adding)
        self.btn_save.clicked.connect(self.controller.save)
        self.line_del.textChanged.connect(self.controller.line_remove_change)
        self.line_add.textChanged.connect(self.controller.line_add_change)
        self.table_model.line_remove_change.connect(self.on_line_remove_change)
        self.table_model.line_add_change.connect(self.on_line_add_change)

    def SetupUI(self):
        self.parent.setGeometry(300, 200, 1350, 550)
        self.parent.setWindowTitle("Приложение")
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.font = QFont("Arial", 14)
        self.table_view.setFont(self.font)
        self.table_view.resizeColumnsToContents()
        self.table_view.setSortingEnabled(True)
        self.layout_main = QGridLayout()
        self.layoutV = QVBoxLayout()
        self.layoutH1 = QHBoxLayout()
        self.layoutH2 = QHBoxLayout()
        self.layoutH3 = QHBoxLayout()
        self.btn_del = QPushButton("Удалить", self.parent)
        self.btn_add = QPushButton("Добавить", self.parent)
        self.btn_save = QPushButton("Сохранить", self.parent)
        self.line_del = QLineEdit(self.parent)
        self.line_add = QLineEdit(self.parent)
        self.layoutH1.addWidget(self.btn_del)
        self.layoutH1.addWidget(self.line_del)
        self.layoutH2.addWidget(self.btn_add)
        self.layoutH2.addWidget(self.line_add)
        self.layoutV.addLayout(self.layoutH1)
        self.layoutV.addLayout(self.layoutH2)
        self.layoutV.addWidget(self.btn_save)
        self.layout_main.addWidget(self.table_view, 0, 0)
        self.layout_main.addLayout(self.layoutV, 1, 0)
        self.parent.setLayout(self.layout_main)
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

    def dels(self):
        self.controller.remove()
        self.table_view.update()

    @Slot(list)
    def on_list_changed(self):
        self.table_view.setBaseSize(
            len(self.table_model.__headers), len(self.table_model.__data_list)
        )

    @Slot(str)
    def on_line_remove_change(self, value):
        self.line_del.setText(value)

    @Slot(str)
    def on_line_add_change(self, value):
        self.line_add.setText(value)


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.model = MyTableModel(self)
        self.main_controller = MyTableController(self.model)
        self.main_view = MyTableView(self, self.model, self.main_controller)


if __name__ == "__main__":
    app = QApplication([])
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())
