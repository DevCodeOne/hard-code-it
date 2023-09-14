import gi
import re

from functools import partial

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hard-Code-It")

        self.template_path = ""

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        self.set_border_width(10)
        self.pattern_list = []
        self.files_to_hardcode = dict()

        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        self.process = Gtk.Stack()
        self.process.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.process.set_transition_duration(400)

        template_selection = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label = Gtk.Label()
        label.set_markup("<big>Choose template file and language</big>")
        replacement_selection = Gtk.ComboBoxText()
        replacement_selection.append_text("Javascript")
        replacement_selection.set_active(0)
        template_file_selection = Gtk.FileChooserButton(action=Gtk.FileChooserAction.OPEN)
        template_file_selection.connect("selection-changed", self.on_drop)
        template_selection.add(label)
        template_selection.add(replacement_selection)
        template_selection.add(template_file_selection)

        self.file_selection = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.process.add_titled(template_selection, "template", "Select template")
        self.process.add_titled(self.file_selection, "files", "Select Files")

        process_switcher = Gtk.StackSwitcher()
        process_switcher.set_stack(self.process)

        vbox.pack_start(process_switcher, True, True, 0)
        vbox.pack_start(self.process, True, True, 0)

    def on_drop(widget, user_data):
        widget.process.set_visible_child_name("files")

        if widget.process.get_visible_child_name() == "files":
            widget.template_path = user_data.get_filename()
            widget.generate_pattern_choosers()
            print("Selected {0} as template file".format(widget.template_path))

    def retrieve_patterns(widget):
        # TODO: add javascript style
        pattern_reg = re.compile(r'(insert)( name:(?P<name>(\w*)) type:(?P<type>(\w*)) count:(?P<count>(\d*|(array))) here)')
        patterns = dict()
        
        with open(widget.template_path) as template:
            template_file = template.read()
            found_patterns = pattern_reg.finditer(template_file)

            for result in found_patterns:
                print(template_file[result.start():result.end()])
                # template_file.replace()
                patterns[result.group("name")] = {"count" : result.group("count"), "type" : result.group("type")}
                print("Found {0} pattern".format(patterns[result.group("name")]))

        return patterns
    
    def generate_pattern_choosers(widget):
        for label in widget.pattern_list:
            widget.file_selection.remove(label)

        widget.pattern_list = []

        pattern_list = widget.retrieve_patterns()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        for pattern in pattern_list.keys():
            if pattern_list[pattern]["count"] == "1":
                print(f"Generated label for %s" % pattern)
                label = Gtk.Label()
                label.set_text(pattern)
                label.set_selectable(False)

                label_file_selection = Gtk.FileChooserButton(action=Gtk.FileChooserAction.OPEN)
                label_file_selection.connect("selection-changed", widget.on_drop)

                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                hbox.set_homogeneous(True)
                hbox.add(label)
                hbox.add(label_file_selection)
                vbox.add(hbox)
            else:
                label = Gtk.Label()
                label.set_text(pattern)
                label.set_selectable(False)

                filechooser_button = Gtk.Button.new_with_label("Select files for pattern {0}".format(pattern))
                filechooser_button.connect("clicked", partial(widget.on_button_clicked, pattern))
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                hbox.set_homogeneous(True)
                hbox.add(label)
                hbox.add(filechooser_button)
                vbox.add(hbox)
        
        widget.pattern_list.append(vbox)
        widget.file_selection.add(vbox)
        widget.file_selection.show_all()

        return
    
    def on_button_clicked(self, argument, button):
        # TODO: fix deprecation warning
        dialog = Gtk.FileChooserDialog("Select files for pattern {0}".format(argument), None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK) )
        dialog.set_select_multiple(True)
        response = dialog.run()
        print("Selected {0} as files for {1}".format(dialog.get_filenames(), argument))
        files_to_hardcode[argument] = dialog.get_filenames()
        dialog.destroy()

        return
    
win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()