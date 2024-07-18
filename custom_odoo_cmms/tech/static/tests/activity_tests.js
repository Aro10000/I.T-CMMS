/** @odoo-module **/

import { start, startServer } from '@mail/../tests/helpers/test_utils';

QUnit.module('tech', () => {
QUnit.module('components', () => {
QUnit.module('activity_tests.js');

QUnit.test('activity click on Reschedule', async function (assert) {
    assert.expect(1);

    const pyEnv = await startServer();
    const resPartnerId = pyEnv['res.partner'].create({});
    const meetingActivityTypeId = pyEnv['mail.activity.type'].create({ icon: 'fa-tech', name: "Meeting" });
    const techAttendeeId = pyEnv['tech.attendee'].create({ partner_id: resPartnerId });
    const calendaMeetingId = pyEnv['tech.event'].create({
        res_model: "tech.event",
        name: "meeting1",
        start: "2022-07-06 06:30:00",
        attendee_ids: [techAttendeeId],
    });
    pyEnv['mail.activity'].create({
        name: "Small Meeting",
        activity_type_id: meetingActivityTypeId,
        can_write: true,
        res_id: resPartnerId,
        res_model: 'res.partner',
        tech_event_id: calendaMeetingId,
    });

    const { click, openFormView } =  await start();

    await openFormView(
        {
            res_model: 'res.partner',
            res_id: resPartnerId,
        },
    );

    await click('.o_Activity_editButton');
    assert.containsOnce(
        document.body,
        '.o_tech_view',
        "should have opened tech view"
    );
});

});
});
