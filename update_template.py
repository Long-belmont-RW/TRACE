import re

with open(r'c:\Users\USER\Documents\Projects\Django\TRACE\Frontend_mockups\prison_officer_dashboard_mockup.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add standard Django tags at the top
html = '{% load i18n static %}\n' + html

# Fix the user profile info
html = html.replace('Sgt. Marcus Thorne', '{{ user.get_full_name|default:user.email }}')
html = html.replace('Officer Role', '{{ user.get_role_display }}')

# Fix logout url
html = html.replace('href="#"', 'href="#"') # keep # for most
html = html.replace('<span class="font-label-md">Logout</span>', '<a href="{% url \'accounts:logout\' %}" class="font-label-md">Logout</a>')

# Fix KPIs
html = html.replace('>1,428<', '>{{ total_inmates }}<')
html = html.replace('>42<', '>{{ total_active_alerts }}<')
html = html.replace('>08<', '>{{ total_escalated_alerts }}<')

# The alerts table
table_pattern = r'<tbody class="divide-y divide-outline-variant">.*?</tbody>'
replacement_tbody = """<tbody class="divide-y divide-outline-variant">
{% for alert in unresolved_alerts %}
<tr class="hover:bg-surface-container-low transition-colors group">
<td class="px-gutter py-4">
<span class="inline-flex items-center px-2 py-1 bg-error text-white text-[10px] font-bold rounded">
{% if alert.is_escalated %}ESCALATED{% else %}90+ DAYS{% endif %}
</span>
</td>
<td class="px-gutter py-4 font-semibold text-on-surface">{{ alert.inmate.first_name }} {{ alert.inmate.last_name }}</td>
<td class="px-gutter py-4 text-on-surface-variant">{{ alert.inmate.inmate_number }}</td>
<td class="px-gutter py-4 text-center font-bold text-error">90+</td>
<td class="px-gutter py-4 text-on-surface-variant">{{ alert.inmate.last_court_update|date:"M d, Y"|default:"N/A" }}</td>
<td class="px-gutter py-4 text-right">
{% if alert.is_escalated %}
<span class="text-xs font-semibold text-error uppercase">Escalated</span>
{% else %}
<button class="bg-primary text-white px-4 py-2 text-xs font-semibold rounded hover:bg-primary-container transition-all shadow-sm" onclick="openEscalationModal('{{ alert.inmate.first_name|escapejs }} {{ alert.inmate.last_name|escapejs }}', '{{ alert.inmate.inmate_number|escapejs }}', '{{ alert.id }}')">Review & Escalate</button>
{% endif %}
</td>
</tr>
{% empty %}
<tr>
<td colspan="6" class="px-gutter py-8 text-center text-on-surface-variant">No active alerts found.</td>
</tr>
{% endfor %}
</tbody>"""

html = re.sub(table_pattern, replacement_tbody.replace('\\', '\\\\'), html, flags=re.DOTALL)

# Modal form changes
modal_body_pattern = r'<div class="p-gutter space-y-6">.*?</div>\s*<!-- Modal Footer -->'
modal_body_replacement = """<form method="POST" action="{% url 'custody:escalate_alert' %}">
{% csrf_token %}
<input type="hidden" name="alert_id" id="escalation-alert-id" value="">
<div class="p-gutter space-y-6">
<div class="bg-error-container bg-opacity-5 p-4 border-l-4 border-error">
<p class="text-on-surface font-body-md">
You are about to escalate the 90-day overdue alert for <strong class="text-error" id="modal-inmate-name"></strong> <span class="text-on-surface-variant text-sm" id="modal-inmate-id"></span> to the Facility Commander.
</p>
</div>
<div class="space-y-2">
<label class="font-label-sm text-on-surface-variant uppercase tracking-wider block" for="escalation-reason">Escalation Reason/Note</label>
<textarea name="note" class="w-full border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded-lg text-body-md placeholder:text-on-surface-variant/50" id="escalation-reason" placeholder="Describe the reason for escalation and any security concerns..." rows="4" required></textarea>
</div>
<div class="bg-surface-container-low p-3 rounded text-[11px] text-on-surface-variant flex gap-2">
<span class="material-symbols-outlined text-sm" data-icon="info">info</span>
This action will be logged in the TRACE Audit System and will immediately notify the duty commander.
</div>
</div>
<!-- Modal Footer -->"""

html = re.sub(modal_body_pattern, modal_body_replacement.replace('\\', '\\\\'), html, flags=re.DOTALL)

# Modal Footer changes (change button to submit and close form)
modal_footer_pattern = r'<!-- Modal Footer -->.*?</div>\s*</div>'
modal_footer_replacement = """<!-- Modal Footer -->
<div class="px-gutter py-4 bg-surface border-t border-outline-variant flex justify-end gap-3">
<button type="button" class="px-6 py-2 border border-outline-variant text-on-surface font-semibold hover:bg-surface-container-low transition-colors rounded" onclick="closeEscalationModal()">Cancel</button>
<button type="submit" class="px-6 py-2 bg-error text-white font-semibold hover:bg-on-error-container transition-colors shadow-sm rounded">Confirm Escalation</button>
</div>
</form>
</div>"""
html = re.sub(modal_footer_pattern, modal_footer_replacement.replace('\\', '\\\\'), html, flags=re.DOTALL)

# Update the JavaScript
js_pattern = r'function openEscalationModal\(name, id\) \{.*?\n\s*\}'
js_replacement = """function openEscalationModal(name, id, alertId) {
            modalInmateName.textContent = name;
            modalInmateId.textContent = id;
            document.getElementById('escalation-alert-id').value = alertId;
            textArea.value = ""; // Clear previous notes
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Prevent scroll
        }"""
html = re.sub(js_pattern, js_replacement.replace('\\', '\\\\'), html, flags=re.DOTALL)

# Remove the confirmEscalation JS function because it's now handled by standard form submission
confirm_js_pattern = r'function confirmEscalation\(\) \{.*?\n\s*\}\n'
html = re.sub(confirm_js_pattern, '', html, flags=re.DOTALL)

# Add django messages block at the start of main
main_pattern = r'<main class="ml-sidebar-width mt-16 p-container-padding">'
messages_block = """<main class="ml-sidebar-width mt-16 p-container-padding">
{% if messages %}
<div class="mb-stack-lg">
    {% for message in messages %}
    <div class="p-4 rounded {% if message.tags == 'success' %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
        {{ message }}
    </div>
    {% endfor %}
</div>
{% endif %}"""
html = html.replace(main_pattern, messages_block)

with open(r'c:\Users\USER\Documents\Projects\Django\TRACE\templates\custody\officer_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Update complete")
