function prepareModal(id, size = 'modal-md') {
    const modal = $(id);
    modal.addClass('modal')
        .addClass('fade')
        .attr('tabindex', '-1')
        .attr('role', 'dialog')
        .attr('aria-labelledby', `${id}-title`);
    modal.html(`<div class="modal-dialog ${size}" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="${id}-title"></h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body text-left"></div>
          <div class="modal-footer"></div>
        </div>
      </div>`)
}


async function openModal(id, apiUrl) {
    const modal = $(id)
    const title = modal.find('.modal-title');
    const body = modal.find('.modal-body');
    const footer = modal.find('.modal-footer');
    body.empty();
    footer.empty();
    body.append($('<div class="spinner-border" role="status"></div>'));
    title.text('Loading...');
    modal.modal('show');
    let data;
    if (apiUrl) {
        if (Array.isArray(apiUrl)) {
            data = await Promise.all(apiUrl.map(url => fetch(url).then(res => res.json())));
        } else {
            data = await fetch(apiUrl).then(res => res.json());
        }
    }else{
        data = null;
    }
    body.empty();
    return {data, title, body, footer};
}

function renderGroupModalBody(body, data) {
    const {
        group_description,
        trainer_first_name,
        trainer_last_name,
        trainer_email,
        capacity,
        current_load,
        training_class,
        hours,
        link_name,
        link
    } = data;
    if (group_description) {
        body.append(`<p>${group_description}</p>`);
    }
    if (link) {
        const label = link_name ? `${link_name}: ` : '';
        body.append(`<p>${label}<a href=${link}>${link}</a></p>`)
    }

    const p = body.append('<p>').children('p:last-child');
    if (capacity) {
        p.append(`<div>Available places: <strong>${capacity - current_load}/${capacity}</strong></div>`);
    }
    if (training_class) {
        p.append(`<div>Class: <strong>${training_class}</strong></div>`);
    }

    if (trainer_first_name || trainer_last_name || trainer_email) {
        body.append(`<p>Trainer: 
                        <strong>${trainer_first_name} ${trainer_last_name}</strong> 
                        <a href="mailto:${trainer_email}">${trainer_email}</a>
                     </p>`);
    }
    if (hours) {
        body.append(`<p>Marked hours: <strong>${hours.toFixed(2)}</strong></p>`);
    }
}

function formatTime(time) {
    return time.substring(0, time.length - 3);
}

async function openGroupInfoModalForStudent(apiUrl, enrollErrorCb = () => 0) {
    const {data, title, body, footer} = await openModal('#group-info-modal', apiUrl)
    const {custom_name, group_id, group_name, is_enrolled, capacity, current_load, is_primary, schedule} = data;

    let disabled_attr;

    if (is_enrolled) {
        disabled_attr =  is_primary ? 'disabled' : '';
        footer.html(`
            <div class="container">
                <div class="row justify-content-between">
                    <div><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button></div>
                    <div><button type="button" class="btn btn-danger ${disabled_attr}" ${disabled_attr}>Unenroll</button></div>
                </div>
            </div>
        `);
        footer.find('.btn-danger').click(() => enroll(group_id, 'unenroll'));
    } else {
        disabled_attr = current_load >= capacity ? 'disabled' : ''
        footer.html(`
            <div class="container">
                <div class="row justify-content-between">
                    <div><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button></div>
                    <div><button type="button" class="btn btn-success ${disabled_attr}" ${disabled_attr}>Enroll</button></div>
                </div>
            </div>
        `);
        footer.find('.btn-success').click(() => enroll(group_id, 'enroll', enrollErrorCb));
    }
    title.text(custom_name || `${group_name} group`);
    renderGroupModalBody(body, data)
    if (schedule && schedule.length > 0) {

        const days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ];
        schedule.sort(
            (a, b) => (a.weekday > b.weekday) ? 1 : (a.start > b.start) ? 1 : -1
        )
        body.append(`
            <strong>Schedule</strong>:<br>    
        `)

        let currentDay = null;

        for (let training of schedule) {
            if (training.weekday !== currentDay) {
                body.append(`<i>${days[training.weekday]}</i>:`);
                currentDay = training.weekday;
            }
            body.append(`<li>${formatTime(training.start)} - ${formatTime(training.end)}</li>`);
        }

    }
    return data;
}

async function unenroll_by_trainer(group_id, student_id) {
    await sendResults('/api/enrollment/unenroll_by_trainer', { group_id, student_id })
    $(`#enrolled-student-${student_id}`).remove()
}

async function openGroupInfoModalForTrainer(apiUrl) {
    const {data, title, body, footer} = await openModal('#group-info-modal', apiUrl);
    footer.html('<div><button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button></div>');
    title.text(`${data[0].group_name} group`);
    renderGroupModalBody(body, data[0]);
    const tbody = body.append(`<p>Enrolled students:
                    <table class="table table-hover table-responsive-md">
                        <thead>
                            <th>Student name</th>
                            <th>Last attended</th>
                            <th>Unenroll</th>
                        </thead>
                    </table>
                 </p>`).find('table').append('<tbody>');
    const last_attended_dates = data[1].last_attended_dates.sort(
        (a, b) => new Date(b.last_attended) - new Date(a.last_attended)
    );
    const icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
      <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4L4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
    </svg>`
    last_attended_dates.forEach(info => {
        tbody.append(`<tr id="enrolled-student-${info.student_id}">
            <td>${info.full_name}</td>
            <td>${info.last_attended ? info.last_attended.split('T')[0] : 'N/A'}</td>
            <td>
                <button class="btn btn-outline-danger" onclick="unenroll_by_trainer(${data[0].group_id}, ${info.student_id})">${icon}</button>
            </td>
        </tr>`)
    });
}
