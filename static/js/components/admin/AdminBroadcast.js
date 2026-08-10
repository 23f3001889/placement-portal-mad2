/**
 * AdminBroadcast.js — admin types a message, picks an audience, 
 * it's queued on Celery (POST /admin/broadcast returns 202 immediately).
 * Demo component:
 * - shows the "queued, not done yet" state, 
 * - then a manual refresh to reveal
 * - the async work has landed once the worker (with its 5s sleep) finishes.
 */
const AdminBroadcast = {
    data: function () {
        return {
            message: '',
            audience: 'student',
            sending: false,
            queued: false,
            result: null,
            error: ''
        };
    },
    methods: {
        send: function () {
            var self = this;
            if (!this.message.trim()) return;

            self.sending = true;
            self.queued = false;
            self.result = null;
            self.error = '';

            return window.api.post('/admin/broadcast', {
                message: this.message,
                audience: this.audience
            })
                .then(function () {
                    self.queued = true;
                    self.message = '';
                })
                .catch(function (err) {
                    self.error = (err.response && err.response.data && err.response.data.msg) || 'Failed to queue broadcast.';
                })
                .finally(function () {
                    self.sending = false;
                });
        }
    },
    template:
        '<div class="container mt-4" style="max-width: 640px;">' +
        '  <h4 class="mb-3"><i class="bi bi-megaphone me-2"></i>Broadcast Message</h4>' +
        '  <p class="text-muted small">' +
        '    Sends a message to every user of the selected role. Queued via Celery — ' +
        '    the worker takes a few seconds, so it won\'t appear instantly.' +
        '  </p>' +
        '' +
        '  <error-alert :message="error" @dismiss="error = \'\'"></error-alert>' +
        '' +
        '  <div v-if="queued" class="alert alert-info">' +
        '    <i class="bi bi-hourglass-split me-2"></i>Broadcast queued — check the recipient\'s ' +
        '    notifications (and Mailhog) in a few seconds.' +
        '  </div>' +
        '' +
        '  <div class="card">' +
        '    <div class="card-body">' +
        '      <div class="mb-3">' +
        '        <label class="form-label">Audience</label>' +
        '        <select class="form-select" v-model="audience">' +
        '          <option value="student">Students</option>' +
        '          <option value="company">Companies</option>' +
        '        </select>' +
        '      </div>' +
        '      <div class="mb-3">' +
        '        <label class="form-label">Message</label>' +
        '        <textarea class="form-control" rows="3" v-model="message" placeholder="e.g. Placement drive results will be announced tomorrow."></textarea>' +
        '      </div>' +
        '      <button class="btn btn-dark" :disabled="sending || !message.trim()" @click="send">' +
        '        <span v-if="sending" class="spinner-border spinner-border-sm me-2"></span>' +
        '        {{ sending ? \'Queuing…\' : \'Send Broadcast\' }}' +
        '      </button>' +
        '    </div>' +
        '  </div>' +
        '</div>'
};