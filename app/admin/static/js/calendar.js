document.addEventListener('DOMContentLoaded', function () {
    let calendarEl = document.getElementById('calendar');
    let eventsData = [
        '{% for event in events %}'
        {
            title: '{{ event[0] }}',
            start: new Date('{{ event[1] }}'), 
            project: '{{ event[2] }}', 
        },
        '{% endfor %}'
    ];

    // Group events by date and remove duplicates
    let groupedEvents = groupAndRemoveDuplicates(eventsData);

    let calendar = new FullCalendar.Calendar(calendarEl, {
        events: groupedEvents,
        eventClick: function (info) {
            const modal = document.getElementById('eventModal');
            const titleElement = document.getElementById('eventTitle');
            const startElement = document.getElementById('eventStart');
            const projectElement = document.getElementById('eventProject');

            titleElement.textContent = info.event.title;
            startElement.textContent = 'Date: ' + info.event.start.toLocaleString();
            projectElement.textContent = 'Project: ' + info.event.extendedProps.project;

            modal.style.display = 'flex';
        }
    });

    calendar.render();

    const modal = document.getElementById('eventModal');
    const closeModal = document.getElementById('closeModal');
    closeModal.addEventListener('click', function (event) {
        modal.style.display = 'none';
    });
    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Function to group events by date and remove duplicates
    function groupAndRemoveDuplicates(events) {
        let grouped = {};
        for (let event of events) {
            let dateStr = event.start.toISOString().split('T')[0];
            if (!grouped[dateStr]) {
                grouped[dateStr] = event;
            }
        }

        // Convert to an array of objects
        let groupedArray = Object.values(grouped);

        return groupedArray;
    }
});