import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QFileDialog, QLabel, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QMenu, QAction
from PyQt5.QtCore import QSettings, Qt

class PreviewDialog(QDialog):
    def __init__(self, rename_data):
        super().__init__()
        self.setWindowTitle('重命名预览')
        self.resize(1200, 800)

        layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['文件夹', '旧文件名', '新文件名'])
        self.table.setRowCount(len(rename_data))

        for row, (folder, old_name, new_name) in enumerate(rename_data):
            self.table.setItem(row, 0, QTableWidgetItem(folder))
            self.table.setItem(row, 1, QTableWidgetItem(old_name))
            self.table.setItem(row, 2, QTableWidgetItem(new_name))

        # 设置表格列宽自适应
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        self.setLayout(layout)

class FileOrganizer(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings('MyApp', 'FileOrganizer')
        self.initUI()

    def initUI(self):
        # 设置窗口初始大小
        self.resize(1200, 800)

        # 主布局
        main_layout = QVBoxLayout()

        # 文件夹选择布局
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self)
        self.import_button = QPushButton('导入', self)
        self.import_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.import_button)

        # 文件夹和文件计数显示
        count_layout = QHBoxLayout()
        self.folder_count_label = QLabel('文件夹数量: 0', self)
        self.file_count_label = QLabel('文件总数: 0', self)
        count_layout.addWidget(self.folder_count_label)
        count_layout.addStretch()

        # 文件列表布局
        list_layout = QHBoxLayout()
        self.left_list = QTreeWidget(self)
        self.left_list.setHeaderHidden(True)
        self.left_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.left_list.customContextMenuRequested.connect(self.open_context_menu)

        # 右侧布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.file_count_label)  # 将文件总数标签放在右侧布局的顶部
        self.right_list = QTreeWidget(self)
        self.right_list.setHeaderHidden(True)
        self.right_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.right_list.customContextMenuRequested.connect(self.open_context_menu_right)
        right_layout.addWidget(self.right_list)

        # 右侧下方布局
        bottom_layout = QHBoxLayout()
        self.replace_checkbox = QCheckBox('查找替换', self)
        self.replace_checkbox.stateChanged.connect(self.toggle_replace)
        self.line_edit = QLineEdit(self)
        self.replace_line_edit = QLineEdit(self)
        self.replace_line_edit.setPlaceholderText('请输入替换内容')
        self.replace_line_edit.setVisible(False)  # 默认隐藏

        self.start_button = QPushButton('开始', self)
        self.start_button.clicked.connect(self.rename_files)
        self.preview_button = QPushButton('预览', self)
        self.preview_button.clicked.connect(self.preview_rename)

        # 新增帮助按钮
        self.help_button = QPushButton('帮助', self)
        self.help_button.clicked.connect(self.show_help)

        bottom_layout.addWidget(self.replace_checkbox)
        bottom_layout.addWidget(self.line_edit)
        bottom_layout.addWidget(self.replace_line_edit)
        bottom_layout.addWidget(self.start_button)
        bottom_layout.addWidget(self.preview_button)
        bottom_layout.addWidget(self.help_button)  # 添加帮助按钮

        # 添加文件类型复选框
        self.jpg_checkbox = QCheckBox('jpg', self)
        self.txt_checkbox = QCheckBox('txt', self)
        self.xml_checkbox = QCheckBox('xml', self)

        # 默认选中所有复选框
        self.jpg_checkbox.setChecked(True)
        self.txt_checkbox.setChecked(True)
        self.xml_checkbox.setChecked(True)

        # 将复选框添加到布局
        bottom_layout.addWidget(self.jpg_checkbox)
        bottom_layout.addWidget(self.txt_checkbox)
        bottom_layout.addWidget(self.xml_checkbox)

        right_layout.addLayout(bottom_layout)

        # 按钮布局
        button_layout = QVBoxLayout()
        self.add_button = QPushButton('增加', self)
        self.add_button.clicked.connect(self.add_to_right)
        self.add_all_button = QPushButton('增加全部', self)
        self.add_all_button.clicked.connect(self.add_all_to_right)
        self.remove_button = QPushButton('移除', self)
        self.remove_button.clicked.connect(self.remove_from_right)
        
        # 新增"移除全部"按钮
        self.remove_all_button = QPushButton('移除全部', self)
        self.remove_all_button.clicked.connect(self.remove_all_from_right)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.add_all_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.remove_all_button)  # 添加"移除全部"按钮

        # 将组件添加到列表布局
        list_layout.addWidget(self.left_list)
        list_layout.addLayout(button_layout)
        list_layout.addLayout(right_layout)

        # 布局设置
        main_layout.addLayout(folder_layout)
        main_layout.addLayout(count_layout)
        main_layout.addLayout(list_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('重命名')

        # 加载上次打开的文件夹
        last_folder = self.settings.value('lastFolder', '')
        if last_folder:
            self.folder_input.setText(last_folder)
            self.populate_left_list(last_folder)

        self.show()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder:
            self.folder_input.setText(folder)
            self.populate_left_list(folder)
            # 保存当前文件夹路径
            self.settings.setValue('lastFolder', folder)

    def populate_left_list(self, folder):
        self.left_list.clear()
        self.right_list.clear()
        folder_count = 0
        for subfolder in os.listdir(folder):
            subfolder_path = os.path.join(folder, subfolder)
            if os.path.isdir(subfolder_path):
                folder_item = QTreeWidgetItem(self.left_list, [subfolder])
                has_files = False  # 用于检查文件夹内是否有文件
                for file in os.listdir(subfolder_path):
                    file_path = os.path.join(subfolder_path, file)
                    if os.path.isfile(file_path):
                        QTreeWidgetItem(folder_item, [file])
                        has_files = True
                if has_files:
                    folder_count += 1
            else:
                # 如果是文件而不是文件夹，直接添加到左侧列表
                QTreeWidgetItem(self.left_list, [subfolder])
                folder_count += 1

        self.folder_count_label.setText(f'文件夹数量: {folder_count}')
        self.update_file_count()

    def add_to_right(self):
        selected_items = self.left_list.selectedItems()
        for item in selected_items:
            # 检查是否为文件夹
            if item.childCount() > 0:
                folder_item = QTreeWidgetItem(self.right_list, [item.text(0)])
                for i in range(item.childCount()):
                    QTreeWidgetItem(folder_item, [item.child(i).text(0)])
            else:
                # 如果是文件，直接添加到右侧列表
                QTreeWidgetItem(self.right_list, [item.text(0)])
        self.update_file_count()

    def add_all_to_right(self):
        self.right_list.clear()
        for i in range(self.left_list.topLevelItemCount()):
            item = self.left_list.topLevelItem(i)
            folder_item = QTreeWidgetItem(self.right_list, [item.text(0)])
            for j in range(item.childCount()):
                QTreeWidgetItem(folder_item, [item.child(j).text(0)])
        self.update_file_count()

    def remove_from_right(self):
        selected_items = self.right_list.selectedItems()
        for item in selected_items:
            index = self.right_list.indexOfTopLevelItem(item)
            self.right_list.takeTopLevelItem(index)
        self.update_file_count()

    def remove_all_from_right(self):
        self.right_list.clear()
        self.update_file_count()

    def update_file_count(self):
        file_count = 0
        for i in range(self.right_list.topLevelItemCount()):
            item = self.right_list.topLevelItem(i)
            if item.childCount() > 0:
                file_count += item.childCount()
            else:
                # 如果是单个文件，直接计数
                file_count += 1
        self.file_count_label.setText(f'文件总数: {file_count}')

    def toggle_replace(self, state):
        self.replace_line_edit.setVisible(state == Qt.Checked)

    def rename_files(self):
        prefix = self.line_edit.text()
        replace_text = self.replace_line_edit.text() if self.replace_checkbox.isChecked() else None
        hash_count = prefix.count('#')

        for i in range(self.right_list.topLevelItemCount()):
            item = self.right_list.topLevelItem(i)
            if item.childCount() > 0:
                # 处理文件夹
                folder_name = item.text(0)
                folder_path = os.path.join(self.folder_input.text(), folder_name)
                parent_folder_name = os.path.basename(os.path.dirname(folder_path))

                for j in range(item.childCount()):
                    file_item = item.child(j)
                    original_name = file_item.text(0)
                    original_path = os.path.join(folder_path, original_name)
                    if self.should_rename_file(original_name):
                        new_name = self.generate_new_name(original_name, prefix, replace_text, parent_folder_name, folder_name, j, hash_count)
                        new_path = os.path.join(folder_path, new_name)
                        self.perform_rename(original_path, new_path)
            else:
                # 处理单个文件
                original_name = item.text(0)
                folder_path = self.folder_input.text()
                original_path = os.path.join(folder_path, original_name)
                parent_folder_name = os.path.basename(os.path.dirname(folder_path))
                if self.should_rename_file(original_name):
                    new_name = self.generate_new_name(original_name, prefix, replace_text, parent_folder_name, os.path.basename(folder_path), i, hash_count)
                    new_path = os.path.join(folder_path, new_name)
                    self.perform_rename(original_path, new_path)

        self.refresh_file_lists()

    def generate_new_name(self, original_name, prefix, replace_text, parent_folder_name, folder_name, index, hash_count):
        if not prefix:
            new_name = original_name
        else:
            if hash_count > 0:
                number_format = f'{{:0{hash_count}d}}'
                new_name = prefix.replace('#' * hash_count, number_format.format(index))
            else:
                new_name = prefix

            new_name = new_name.replace('$$p', f'{parent_folder_name}_{folder_name}')
            new_name = new_name.replace('$p', folder_name)
            
            file_extension = os.path.splitext(original_name)[1]

            if '*' in prefix:
                new_name += original_name
            else:
                new_name += file_extension

            new_name = new_name.replace('*', '')

            if replace_text:
                new_name = original_name.replace(prefix, replace_text)

        return new_name

    def perform_rename(self, original_path, new_path):
        print(f'Trying to rename: {original_path} to {new_path}')
        if not os.path.exists(original_path):
            print(f'File does not exist: {original_path}')
            return

        try:
            os.rename(original_path, new_path)
            print(f'Renamed {os.path.basename(original_path)} to {os.path.basename(new_path)}')
        except Exception as e:
            print(f'Error renaming {os.path.basename(original_path)}: {e}')

    def refresh_file_lists(self):
        # 重新填充左侧列表
        current_folder = self.folder_input.text()
        if current_folder:
            self.populate_left_list(current_folder)

    def preview_rename(self):
        rename_data = []
        prefix = self.line_edit.text()
        replace_text = self.replace_line_edit.text() if self.replace_checkbox.isChecked() else None
        hash_count = prefix.count('#')

        for i in range(self.right_list.topLevelItemCount()):
            item = self.right_list.topLevelItem(i)
            if item.childCount() > 0:
                folder_name = item.text(0)
                folder_path = os.path.join(self.folder_input.text(), folder_name)
                parent_folder_name = os.path.basename(os.path.dirname(folder_path))

                for j in range(item.childCount()):
                    file_item = item.child(j)
                    original_name = file_item.text(0)
                    if self.should_rename_file(original_name):  # 仅在需要重命名时添加到预览数据
                        new_name = self.generate_new_name(original_name, prefix, replace_text, parent_folder_name, folder_name, j, hash_count)
                        rename_data.append((folder_path, original_name, new_name))
            else:
                # 处理单个文件
                original_name = item.text(0)
                folder_path = self.folder_input.text()
                parent_folder_name = os.path.basename(os.path.dirname(folder_path))
                if self.should_rename_file(original_name):  # 仅在需要重命名时添加到预览数据
                    new_name = self.generate_new_name(original_name, prefix, replace_text, parent_folder_name, os.path.basename(folder_path), i, hash_count)
                    rename_data.append((folder_path, original_name, new_name))

        if rename_data:
            dialog = PreviewDialog(rename_data)
            dialog.exec_()
        else:
            print("没有可预览的重命名数据")

    def should_rename_file(self, filename):
        # 检查文件后缀是否需要重命名
        if filename.endswith('.jpg') and not self.jpg_checkbox.isChecked():
            return False
        if filename.endswith('.txt') and not self.txt_checkbox.isChecked():
            return False
        if filename.endswith('.xml') and not self.xml_checkbox.isChecked():
            return False
        if filename.endswith('.png') and not self.jpg_checkbox.isChecked():
            return False
        return True

    def show_help(self):
        help_text = (
            "整体的使用方法类似于faststoneview\n"
            "# 是数字\n"
            "* 表示保存原始文件名\n"
            "$p 表示文件夹名\n"
            "$$p 表示两级文件夹名"
        )
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle('帮助')
        layout = QVBoxLayout()
        label = QLabel(help_text, help_dialog)
        layout.addWidget(label)
        help_dialog.setLayout(layout)
        help_dialog.exec_()

    def open_context_menu(self, position):
        menu = QMenu()
        open_folder_action = QAction('在文件资源管理器中打开', self)
        open_folder_action.triggered.connect(self.open_folder_in_explorer)
        menu.addAction(open_folder_action)
        menu.exec_(self.left_list.viewport().mapToGlobal(position))

    def open_context_menu_right(self, position):
        menu = QMenu()
        open_folder_action = QAction('在文件资源管理器中打开', self)
        open_folder_action.triggered.connect(self.open_folder_in_explorer_right)
        menu.addAction(open_folder_action)
        menu.exec_(self.right_list.viewport().mapToGlobal(position))

    def open_folder_in_explorer(self):
        selected_items = self.left_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            folder_name = item.text(0)
            folder_path = os.path.join(self.folder_input.text(), folder_name)
            if os.path.isdir(folder_path):
                os.startfile(folder_path)
            else:
                print(f"{folder_path} 不是一个有效的文件夹路径")

    def open_folder_in_explorer_right(self):
        selected_items = self.right_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            folder_name = item.text(0)
            folder_path = os.path.join(self.folder_input.text(), folder_name)
            if os.path.isdir(folder_path):
                os.startfile(folder_path)
            else:
                print(f"{folder_path} 不是一个有效的文件夹路径")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileOrganizer()
    sys.exit(app.exec_())