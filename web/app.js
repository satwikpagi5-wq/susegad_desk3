const $ = (selector) => document.querySelector(selector);
const form = $('#guest-form');
let guests = [];

function fields() {
  return Object.fromEntries(['full_name', 'age', 'address', 'id_type', 'id_number']
    .map((key) => [key, form.elements.namedItem(key).value.trim()]));
}

function escaped(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);
}

$('#sample').addEventListener('click', () => {
  form.elements.full_name.value = 'Anaya Fernandes';
  form.elements.age.value = '34';
  form.elements.address.value = 'Sample address, Panaji, Goa';
  form.elements.id_type.value = 'Passport';
  form.elements.id_number.value = '';
  $('#verified').checked = false;
  $('#save').disabled = true;
  $('#status').textContent = 'Fictional sample loaded. Review it, then confirm to add it.';
});

$('#verified').addEventListener('change', () => {
  $('#save').disabled = !$('#verified').checked || !form.elements.full_name.value.trim();
});

form.addEventListener('input', () => {
  if ($('#verified').checked) $('#save').disabled = !form.elements.full_name.value.trim();
});

form.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!$('#verified').checked) return;
  guests.push({ ...fields(), created: new Date() });
  form.reset();
  render();
  $('#status').textContent = 'Demo entry added to this tab’s register.';
});

function render() {
  $('#count').textContent = guests.length;
  $('#empty').classList.toggle('hidden', guests.length > 0);
  $('#export').disabled = !guests.length;
  $('#rows').innerHTML = guests.map((guest, index) => `
    <div class="guest-row">
      <div><strong>${escaped(guest.full_name)}</strong><small>${escaped(guest.id_type || 'Type not specified')} · ${guest.created.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small></div>
      <div>${escaped(guest.address || 'No address')}<small>${guest.id_number ? 'ID ending ' + escaped(guest.id_number.slice(-4)) : 'Demo: no ID number'}</small></div>
      <button class="remove" data-index="${index}" type="button">Remove</button>
    </div>`).join('');
}

$('#rows').addEventListener('click', (event) => {
  if (event.target.matches('.remove')) {
    guests.splice(Number(event.target.dataset.index), 1);
    render();
  }
});

$('#clear-register').addEventListener('click', () => {
  guests = [];
  render();
  $('#status').textContent = 'Demo register cleared.';
});

$('#export').addEventListener('click', () => {
  const columns = ['full_name', 'age', 'address', 'id_type', 'id_number'];
  const csvValue = (value) => {
    let safe = String(value || '');
    if (/^[\s]*[=+\-@]/.test(safe)) safe = `'${safe}`;
    return `"${safe.replaceAll('"', '""')}"`;
  };
  const csv = [columns.join(','), ...guests.map((guest) => columns.map((column) => csvValue(guest[column])).join(','))].join('\r\n');
  const url = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = `susegad-demo-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
  URL.revokeObjectURL(url);
});
