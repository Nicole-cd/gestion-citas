///imprimir reportes
function imprimirReporte() {
    window.print();
}


///seleccionar servicios en reservar cita
document.getElementById('selectFreelancer').addEventListener('change', function () {
    const freelancerId = this.value;
    const servicioSelect = document.getElementById('selectServicio');
    const servicioInfo = document.getElementById('servicioInfo');

    const todasOpciones = servicioSelect.querySelectorAll('option');
    let serviciosEncontrados = 0;

    todasOpciones.forEach(option => {
        option.style.display = 'none';
    });

    if (freelancerId) {
        todasOpciones.forEach(option => {
            const dataFreelancer = option.getAttribute('data-freelancer');
            if (dataFreelancer === freelancerId) {
                option.style.display = 'block';
                serviciosEncontrados++;
            }
        });

        const primeraOpcion = servicioSelect.querySelector('option[style*="display: block"]');
        if (primeraOpcion) {
            servicioSelect.value = primeraOpcion.value;
            servicioInfo.textContent = `${serviciosEncontrados} servicios disponibles.`;
        } else {
            servicioSelect.value = '';
            servicioInfo.textContent = 'Este freelancer no tiene servicios registrados.';
        }
    } else {
        servicioSelect.value = '';
        servicioInfo.textContent = 'Selecciona un freelancer para ver sus servicios.';
    }
});

document.getElementById('formReserva').addEventListener('submit', function (e) {
    const hora = document.getElementById('inputHora').value;
    if (hora < '09:00' || hora > '17:00') {
        e.preventDefault();
        alert('El horario debe estar entre 9:00 AM y 5:00 PM');
    }
});

function segunDisponibilidad() {
    var rol = document.getElementById('id_rol').value;
    var bloque = document.getElementById('bloque-disponibilidad');
    if (rol === 'freelancer') {
        bloque.style.display = 'block';
    } else {
        bloque.style.display = 'none';
    }
}


document.addEventListener('DOMContentLoaded', function () {
    toggleDisponibilidad();
});

