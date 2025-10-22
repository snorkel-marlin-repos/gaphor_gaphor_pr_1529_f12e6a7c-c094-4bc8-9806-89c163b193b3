"""State items property pages.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""
from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_resource_builder,
)

new_builder = new_resource_builder("gaphor.UML.states")


@PropertyPages.register(UML.Transition)
class TransitionPropertyPage(PropertyPageBase):
    """Transition property page allows to edit guard specification."""

    order = 15

    subject: UML.Transition

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject.watcher()

    def construct(self):
        subject = self.subject
        if not subject:
            return

        builder = new_builder(
            "transition-editor",
            signals={
                "transition-destroy": (self.watcher.unsubscribe_all,),
            },
        )

        guard = builder.get_object("guard")
        if subject.guard:
            guard.set_text(subject.guard.specification or "")

        @handler_blocking(guard, "changed", self._on_guard_change)
        def handler(event):
            if event.element is subject.guard and guard.get_text() != event.new_value:
                guard.set_text(event.new_value or "")

        self.watcher.watch("guard[Constraint].specification", handler)

        return builder.get_object("transition-editor")

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        if not self.subject.guard:
            self.subject.guard = self.subject.model.create(UML.Constraint)
        self.subject.guard.specification = value


@PropertyPages.register(UML.State)
class StatePropertyPage(PropertyPageBase):
    """State property page."""

    order = 15
    subject: UML.State

    def __init__(self, subject):
        self.subject = subject

    def construct(self):
        subject = self.subject
        if not subject:
            return

        builder = new_builder(
            "state-editor",
            signals={
                "entry-changed": (self.on_text_change, self.set_entry),
                "exit-changed": (self.on_text_change, self.set_exit),
                "do-activity-changed": (self.on_text_change, self.set_do_activity),
            },
        )

        entry = builder.get_object("entry")
        if subject.entry:
            entry.set_text(subject.entry.name or "")

        exit = builder.get_object("exit")
        if subject.exit:
            exit.set_text(subject.exit.name or "")

        do_activity = builder.get_object("do-activity")
        if subject.doActivity:
            do_activity.set_text(self.subject.doActivity.name or "")

        return builder.get_object("state-editor")

    @transactional
    def on_text_change(self, entry, method):
        value = entry.get_text().strip()
        method(value)

    def set_entry(self, text):
        if not self.subject.entry:
            self.subject.entry = self.subject.model.create(UML.Activity)
        self.subject.entry.name = text

    def set_exit(self, text):
        if not self.subject.exit:
            self.subject.exit = self.subject.model.create(UML.Activity)
        self.subject.exit.name = text

    def set_do_activity(self, text):
        if not self.subject.doActivity:
            self.subject.doActivity = self.subject.model.create(UML.Activity)
        self.subject.doActivity.name = text
