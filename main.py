import gi
import re
import os.path

from base64 import standard_b64encode
from shutil import copyfile

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class MultipleFilesChooser(Gtk.Box):
    def __init__(self, num_files, pattern, text, set_target_callback):
        Gtk.Box.__init__(self)
        self.set_homogeneous(True)

        self.pattern = pattern
        self.text = text
        self.set_target_callback = set_target_callback

        target_list = Gtk.TargetList()
        target_list.add_uri_targets(0)

        self.target_list = list()
        self.button = Gtk.Button.new_with_label(self.text)
        self.button.connect("clicked", self.on_button_clicked)
        self.button.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.button.drag_dest_set_target_list(target_list)
        self.button.connect("drag-data-received", self.on_drop_button)
        self.has_files_icon = Gtk.Image.new_from_icon_name("none", 4)
        self.has_files_icon.set_halign(Gtk.Align.END)

        self.add(self.button)
        self.add(self.has_files_icon)
        return
    
    def get_targets(self):
        return self.targets
    
    def set_targets(self, new_targets):
        print("Selected {0} as files for {1}".format(new_targets, self.pattern))
        self.target_list = new_targets
        self.has_files_icon.set_from_icon_name("checkmark", 4)
        self.set_target_callback(self.pattern, self.target_list)
    
    def has_targets(self):
        return len(self.target_list) > 0

    def on_button_clicked(self, button):
        # TODO: fix deprecation warning
        dialog = Gtk.FileChooserDialog(self.text, None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK) )
        dialog.set_select_multiple(True)
        response = dialog.run()
        self.set_targets(dialog.get_filenames())
        dialog.destroy()
        return
    
    def on_drop_button(self, widget, drag_context, x, y, data, info, time):
        self.set_targets(data.get_uris())

class MainWindow(Gtk.Assistant):
    def __init__(self):
        super().__init__(title="Hard-Code-It")

        self.template_path = ""

        self.set_border_width(10)
        self.pattern_file_chooser = []
        self.pattern_keys = []
        self.to_insert = dict()

        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)
        self.set_size_request(800, 600)

        self.process = Gtk.Assistant()

        label = Gtk.Label()
        label.set_markup("<big>Choose template file and language</big>")
        replacement_selection = Gtk.ComboBoxText()
        replacement_selection.append_text("Javascript")
        replacement_selection.set_active(0)
        template_file_selection = Gtk.FileChooserButton(action=Gtk.FileChooserAction.OPEN)
        template_file_selection.connect("selection-changed", self.on_drop)

        self.file_selection = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.template_selection = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.template_selection.add(label)
        self.template_selection.add(replacement_selection)
        self.template_selection.add(template_file_selection)

        self.finalize_selection = Gtk.Grid()
        self.finalize_selection.set_row_spacing(5)
        self.finalize_selection.set_column_spacing(5)
        self.finalize_selection.set_column_homogeneous(True)
        self.copy_switch_label = Gtk.Label("Copy files to destination")
        self.copy_switch_label.set_halign(Gtk.Align.START)
        self.copy_files_switch = Gtk.Switch()
        self.copy_files_switch.set_valign(Gtk.Align.CENTER)
        self.copy_files_switch.set_halign(Gtk.Align.END)
        self.copy_files_switch.set_hexpand(False)
        self.choose_destination_button = Gtk.FileChooserButton(action=Gtk.FileChooserAction.SELECT_FOLDER)
        self.choose_destination_button.connect("selection-changed", self.on_destination_changed)
        self.do_button = Gtk.Button.new_with_label("Start hardcoding")
        self.do_button.set_sensitive(False)
        self.do_button.connect("clicked", self.on_finalize)
        self.finalize_selection.attach(self.copy_switch_label, 0, 0, 5, 1)
        self.finalize_selection.attach(self.copy_files_switch, 5, 0, 1, 1)
        self.finalize_selection.attach(self.choose_destination_button, 0, 1, 6, 1)
        self.finalize_selection.set_row_baseline_position(6, Gtk.BaselinePosition.BOTTOM)
        self.finalize_selection.attach(self.do_button, 0, 6, 6, 1)

        # self.process.add_titled(template_selection, "template", "Select template")
        self.template_selection_index = self.append_page(self.template_selection)
        # self.process.add_titled(self.file_selection, "files", "Select Files")
        self.append_page(self.file_selection)
        self.append_page(self.finalize_selection)

        self.set_page_title(self.template_selection, "Select template")
        self.set_page_title(self.file_selection, "Select files")
        self.set_page_title(self.finalize_selection, "Finalize")
        self.connect("cancel", self.on_cancel)

    def on_cancel(widget, user_data):
        # TODO: Is this correct ?
        exit(0)

    def on_drop(widget, user_data):
        # widget.process.set_visible_child_name("files")
        widget.set_page_complete(widget.template_selection, True)

        if widget.get_current_page() == widget.template_selection_index:
            widget.template_path = user_data.get_filename()
            widget.generate_pattern_choosers()
            print("Selected {0} as template file".format(widget.template_path))
    
    def retrieve_patterns(self):
        # TODO: add javascript style
        pattern_reg = re.compile(r'(insert)( name:(?P<name>(\w*)) type:(?P<type>(\w*)) count:(?P<count>(\d*|(array))) here)')
        patterns = dict()
        
        with open(self.template_path) as template:
            template_file = template.read()
            found_patterns = pattern_reg.finditer(template_file)

            for result in found_patterns:
                print(template_file[result.start():result.end()])
                # template_file.replace()
                patterns[result.group("name")] = {"count" : result.group("count"), "type" : result.group("type")}
                print("Found {0} pattern".format(patterns[result.group("name")]))

        return patterns
    
    def set_target_callback(self, pattern, uri_list):
        print("Got callback for pattern {0}, with files {1}".format(pattern, uri_list))
        self.to_insert[pattern] = uri_list

        continue_page = True
        for pattern in self.pattern_keys:
            if pattern not in self.to_insert.keys():
                print("Pattern {0} not in keys {1}".format(pattern, self.to_insert.keys()))
                continue_page = False
                break

            if self.to_insert[pattern] == []:
                print(self.to_insert[pattern])
                continue_page = False


        print("Continue ? {0}".format(continue_page))
        if continue_page:
            self.set_page_complete(self.file_selection, True)

        return
    
    def generate_pattern_choosers(widget):
        for label in widget.pattern_file_chooser:
            widget.file_selection.remove(label)

        widget.pattern_file_chooser = []
        widget.pattern_keys = []

        pattern_file_chooser = widget.retrieve_patterns()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        for pattern in pattern_file_chooser.keys():
            widget.pattern_keys.append(pattern)
            # Array type, which can accept a number of files, for now limited to this veeery large number
            count = 10000000

            if pattern_file_chooser[pattern]["count"] != "array":
                count = int(pattern_file_chooser[pattern]["count"])

            filechooser = MultipleFilesChooser(pattern_file_chooser[pattern]["count"], pattern, "Select files for pattern {0}".format(pattern), widget.set_target_callback)
            vbox.add(filechooser)
        
        widget.pattern_file_chooser.append(vbox)
        widget.file_selection.add(vbox)
        widget.file_selection.show_all()

        return


    def on_destination_changed(self, user_data):
        self.destination_path = user_data.get_filename()
        self.do_button.set_sensitive(True)
        return

    def insert_binary_file(self, out_file, filename):
        with open(filename, "rb") as toinsert:
            all_bytes = toinsert.read()
            out_file.write(standard_b64encode(all_bytes).decode('utf-8'))
        return

    def insert_text_file(self, out_file, filename):
        with open(filename) as toinsert:
            complete_file = toinsert.read()
            out_file.write('`{0}`'.format(complete_file))
        return

    def insert_here(self, out_file, name, pattern_values):
        # can be an uri, or a regular string for now
        print("Insert here")
        to_insert = self.to_insert[name]

        # TODO: add syntax of arrays if necessary, e.g. count > 1, or array
        for current_file_to_insert in to_insert:
            if current_file_to_insert.startswith("file://"):
                current_file_to_insert = current_file_to_insert.removeprefix("file://")
            
            if pattern_values["type"] == "binary":
                self.insert_binary_file(out_file, current_file_to_insert)
            else:
                self.insert_text_file(out_file, current_file_to_insert)

            # out_file.write('"{0}"'.format(current_file_to_insert))


        return

    def on_finalize(self, button):
        # TODO: add javascript style
        pattern_reg = re.compile(r'(\/\*\s*)(insert)( name:(?P<name>(\w*)) type:(?P<type>(\w*)) count:(?P<count>(\d*|(array))) here)(\s*\*\/)')
        patterns = dict()

        # TODO: check destination path not template bath, otherwise it will be overwritten
        out_file = open(os.path.join(self.destination_path, os.path.basename(self.template_path)), "wt")
        files_to_copy = list()
        
        with open(self.template_path) as template:
            template_file = template.read()
            found_patterns = pattern_reg.finditer(template_file)

            next_read_begin = 0
            for result in found_patterns:
                out_file.write(template_file[next_read_begin:result.start()])
                next_read_begin = result.end()

                patterns[result.group("name")] = {"count" : result.group("count"), "type" : result.group("type")}
                self.insert_here(out_file, result.group("name"), patterns[result.group("name")])
                files_to_copy.append(self.to_insert[result.group("name")])

            out_file.write(template_file[next_read_begin:len(template_file) - 1])

        if self.copy_files_switch.get_state():
            print(f"Copying files : %s " % files_to_copy)
            for pattern_file_list in files_to_copy:
                for current_file in pattern_file_list:
                    file_destination = os.path.join(self.destination_path, os.path.basename(current_file))
                    copyfile(current_file, file_destination)

        return
    
win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()