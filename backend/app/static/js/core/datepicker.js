// The calendar + time picker (flatpickr, vendored in static/vendor) used by every date field.
// An input marked data-picker="datetime" or data-picker="date" keeps its plain value ("2026-10-28T15:41" / "2026-10-28")
// for the code that reads it, and flatpickr shows a friendly copy next to it ("October 28, 2026 03:41 PM").

export function enhanceDates(root = document) {
  const flatpickr = window.flatpickr;
  if (!flatpickr) return; // the plain text field still works if the script did not load

  root.querySelectorAll('input[data-picker]').forEach((input) => {
    if (input._flatpickr) return;
    const withTime = input.dataset.picker === 'datetime';
    const dialog = input.closest('dialog'); // a dialog sits on top of the page: the calendar has to live inside it

    flatpickr(input, {
      enableTime: withTime,
      dateFormat: withTime ? 'Y-m-d\\TH:i' : 'Y-m-d',
      altInput: true,
      altFormat: withTime ? 'F j, Y  h:i K' : 'M j, Y',
      altInputClass: `${input.className} cursor-pointer`,
      time_24hr: false,
      minuteIncrement: 1,
      disableMobile: true,
      monthSelectorType: 'dropdown',
      appendTo: dialog || undefined,
      // Inside a dialog the calendar is fixed to the screen, so the dialog's own scrolling never hides it.
      position: dialog ? placeInViewport : 'auto',
      defaultDate: input.value || null,
    });
  });
}

function placeInViewport(self) {
  const cal = self.calendarContainer;
  const box = (self.altInput || self._input).getBoundingClientRect();
  cal.style.position = 'fixed';
  const width = cal.offsetWidth, height = cal.offsetHeight;
  const below = box.bottom + 4;
  const top = below + height > innerHeight && box.top - height - 4 > 0 ? box.top - height - 4 : below;
  cal.style.top = `${Math.max(4, top)}px`;
  cal.style.left = `${Math.min(Math.max(4, box.left), innerWidth - width - 4)}px`;
  cal.style.right = 'auto';
}

/** Empty the field without firing change events (the caller reloads once). */
export function clearDate(input) {
  if (input._flatpickr) input._flatpickr.clear(false);
  else input.value = '';
}

/** The visible field of a picker, so an error can be shown on it. */
export const visibleInput = (input) => input?._flatpickr?.altInput || input;
