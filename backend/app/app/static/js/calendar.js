// let f = require("@fullcalendar/core");
// let d = require("@fullcalendar/daygrid");
// let t = require("@fullcalendar/timegrid");

const colors = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#b4005a',
    '#7f7f7f',
    '#7b7c1f',
    '#157786',
];

const color_limit = colors.length;
var color_ptr = 0;

var group_colors = {};

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}


function get_color(group) {
    if (group_colors.hasOwnProperty(group)) {
        // Keep it to assign consistent colors
    } else if (color_ptr < color_limit) {
        // Start assigning colors from the list
        group_colors[group] = colors[color_ptr];
        color_ptr += 1;
        return group_colors[group];
    } else {
        // If it happen that we finished the list - assign random colors
        group_colors[group] = getRandomColor();
    }
    return group_colors[group];

}

async function sendResults(url, data) {
    let response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify(data),
        // headers: {
        //     // 'Content-Type': 'application/json'
        // }
    });
    return await response.json();
}

function goto_profile() {
    window.location.href = "/profile";
}

async function open_modal(eventClickInfo) {
    const {event} = eventClickInfo
    const modal = $('#training-info-modal .modal-body');
    modal.empty();
    modal.append($('<div class="spinner-border" role="status"></div>'));
    $('#training-info-modal').modal('show');
    const response = await fetch(`/api/training/${event.extendedProps.id}`, {
        method: 'GET'
    });
    const {group_description, trainer_first_name, trainer_last_name, trainer_email, is_enrolled} = await response.json();
    $('#enroll-unenroll-btn')
        .attr('data-group-id', event.extendedProps.group_id)
        .attr('data-action', is_enrolled ? 'unenroll' : 'enroll')
        .text(is_enrolled ? "Unenroll" : "Enroll")
        .addClass(is_enrolled ? "btn-danger" : "btn-success")
        .removeClass(is_enrolled ? "btn-success" : "btn-danger");
    $('#info-group-name').text(event.title);
    modal.empty();
    if (group_description) {
        modal.append(`<p>${group_description}</p>`)
    }
    const p = modal.append('<p>').children('p:last-child')
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    p.append(`<div>Weekday and time: <strong>${days[event.start.getDay()]}, ${event.start.toJSON().slice(11, 16)}-${event.end.toJSON().slice(11, 16)}</strong></div>`)
    p.append(`<div>Available places: <strong>${event.extendedProps.capacity - event.extendedProps.currentLoad}/${event.extendedProps.capacity}</strong></div>`)
    if (event.extendedProps.training_class) {
        p.append(`<div>Class: <strong>${event.extendedProps.training_class}</strong></div>`)
    }
    if (trainer_first_name || trainer_last_name || trainer_email) {
        modal.append(`<p>Trainer: <strong>${trainer_first_name} ${trainer_last_name}</strong> <a href="mailto:${trainer_email}">${trainer_email}</a></p>`)
    }
}

function enroll(elem) {
    const group_id = parseInt($(elem).attr('data-group-id'));
    const action = $(elem).attr('data-action');
    sendResults(`/api/${action}`, {group_id: group_id})
        .then(data => {
            if (data.ok) {
                goto_profile();
            } else {
                switch (data.error.code) {
                    // Not a student account
                    case 3:
                    // Deadline passed
                    case 4:
                        goto_profile();
                        break;
                    //The group is full
                    case 2:
                        eventClickInfo.el.style.backgroundColor = '#ff0000';
                        break;
                }
                alert(data.error.description);
            }
        });
}


function render(info) {
    let element = info.el;
    let event = info.event;

    let props = event.extendedProps;
    let available = props.capacity - props.currentLoad;
    element.style.fontSize = "99";
    if (available <= 0) {
        element.style.backgroundColor = "#ff0000"
    } else {
        element.style.backgroundColor = get_color(props.group_id)
    }

    if (props.training_class) {
        $(element).children(".fc-content").append($(`<div>${props.training_class}</div>`))
    }
}

function showCapacity(mouseEnterInfo) {
    let props = mouseEnterInfo.event.extendedProps;
    mouseEnterInfo.el.title = "Available: " + (props.capacity - props.currentLoad) + " / " + props.capacity;
}

document.addEventListener('DOMContentLoaded', function () {
    let calendarEl = document.getElementById('calendar');

    let calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: ['timeGrid'],
        defaultView: 'timeGridWeek',
        header: {
            left: 'title',
            center: '',
            right: ''
            // right: 'today, prev, next'
        },
        height: 'auto',
        timeZone: 'Europe/Moscow',
        firstDay: 1,
        allDaySlot: false,
        slotDuration: '00:30:00',
        minTime: '08:00:00',
        maxTime: '21:00:00',
        defaultTimedEventDuration: '01:30',
        eventClick: open_modal,
        eventMouseEnter: showCapacity,
        eventRender: render,
        // Event format: yyyy-mm-dd
        // TODO: at backend use a loop of 10 standard colors as matplotlib do ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        events: '/api/calendar/' + calendarEl.getAttribute('data-sport') + '/schedule'

    });

    calendar.render();
});
