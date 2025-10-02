/**
 * Gestor de filtros para la lista de tareas
 * 
 * Proporciona funcionalidad para filtrar tareas por tipo (General, Específica, Todas)
 * y mantener la selección del filtro entre navegaciones.
 */

class GestorFiltroTareas {
    constructor() {
        this.tipoFiltro = null;
        this.contadorMostradas = null;
        this.contadorTotal = null;
        this.tablaBody = null;
        this.formsToWatch = [];
        
        this.init();
    }

    /**
     * Inicializa el gestor de filtros
     */
    init() {
        // Esperar a que el DOM esté completamente cargado
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupElements());
        } else {
            this.setupElements();
        }
        
        // Configurar restauración del filtro al cargar la página
        window.addEventListener('load', () => this.restaurarFiltro());
    }

    /**
     * Configura las referencias a elementos del DOM
     */
    setupElements() {
        this.tipoFiltro = document.getElementById("tipoFiltro");
        this.contadorMostradas = document.getElementById("contadorMostradas");
        this.contadorTotal = document.getElementById("contadorTotal");
        this.tablaBody = document.querySelector("tbody");

        if (!this.tipoFiltro) {
            console.warn('Elemento tipoFiltro no encontrado');
            return;
        }

        this.setupEventListeners();
        this.filtrarTareas(); // Aplicar filtro inicial
    }

    /**
     * Configura los event listeners
     */
    setupEventListeners() {
        // Event listener para cambios en el filtro
        this.tipoFiltro.addEventListener("change", () => this.filtrarTareas());

        // Configurar formularios para guardar filtro al enviar
        this.formsToWatch = [
            document.querySelector('form[action="/assignGeneral"]'),
            document.querySelector('form[action="/assignEspecifica"]'),
            document.querySelector('form[action="/refresh"]')
        ];

        this.formsToWatch.forEach(form => {
            if (form) {
                form.addEventListener('submit', () => this.guardarFiltroActual());
            }
        });
    }

    /**
     * Aplica el filtro seleccionado a la tabla de tareas
     */
    filtrarTareas() {
        if (!this.tipoFiltro || !this.tablaBody) {
            return;
        }

        const filtroSeleccionado = this.tipoFiltro.value;
        const filas = this.tablaBody.querySelectorAll("tr");
        let contadorVisibles = 0;

        filas.forEach(fila => {
            // Saltar la fila de "Sin tareas para mostrar" si existe
            if (fila.querySelector("td[colspan]")) {
                return;
            }

            const celdaTipo = fila.querySelector("td:nth-child(2)");
            if (!celdaTipo) return;

            const tipoTarea = celdaTipo.textContent.trim().toLowerCase();
            const mostrarFila = this.evaluarFiltro(filtroSeleccionado, tipoTarea);

            if (mostrarFila) {
                fila.style.display = "";
                contadorVisibles++;
            } else {
                fila.style.display = "none";
            }
        });

        this.actualizarContador(contadorVisibles);
        this.manejarMensajeSinTareas(contadorVisibles);
    }

    /**
     * Evalúa si una tarea debe mostrarse según el filtro seleccionado
     * @param {string} filtro - El filtro seleccionado
     * @param {string} tipoTarea - El tipo de tarea en minúsculas
     * @returns {boolean} - True si debe mostrarse, false en caso contrario
     */
    evaluarFiltro(filtro, tipoTarea) {
        switch(filtro) {
            case "todas":
                return true;
            case "general":
                return tipoTarea.includes("general");
            case "specific":
                return tipoTarea.includes("specific");
            default:
                return true;
        }
    }

    /**
     * Actualiza el contador de tareas mostradas
     * @param {number} contadorVisibles - Número de tareas visibles
     */
    actualizarContador(contadorVisibles) {
        if (this.contadorMostradas) {
            this.contadorMostradas.textContent = contadorVisibles;
        }
    }

    /**
     * Maneja la visualización del mensaje cuando no hay tareas que mostrar
     * @param {number} contadorVisibles - Número de tareas visibles
     */
    manejarMensajeSinTareas(contadorVisibles) {
        const filaSinTareas = this.tablaBody?.querySelector("td[colspan]");
        if (!filaSinTareas) return;

        const filaPadre = filaSinTareas.parentElement;
        const totalTareas = this.contadorTotal?.textContent || "0";

        if (contadorVisibles === 0 && totalTareas !== "0") {
            filaPadre.style.display = "";
            filaSinTareas.textContent = "No hay tareas que coincidan con el filtro seleccionado";
        } else if (totalTareas === "0") {
            filaPadre.style.display = "";
            filaSinTareas.textContent = "Sin tareas para mostrar";
        } else {
            filaPadre.style.display = "none";
        }
    }

    /**
     * Guarda el filtro actual en localStorage
     */
    guardarFiltroActual() {
        if (this.tipoFiltro) {
            localStorage.setItem('filtroTareas', this.tipoFiltro.value);
        }
    }

    /**
     * Restaura el filtro guardado desde localStorage
     */
    restaurarFiltro() {
        const filtroGuardado = localStorage.getItem('filtroTareas');
        if (filtroGuardado && this.tipoFiltro) {
            this.tipoFiltro.value = filtroGuardado;
        }
        this.filtrarTareas();
    }

    /**
     * Método público para refrescar el filtrado (útil después de actualizaciones de datos)
     */
    refrescar() {
        this.filtrarTareas();
    }

    /**
     * Método público para cambiar el filtro programáticamente
     * @param {string} nuevoFiltro - El nuevo filtro a aplicar
     */
    cambiarFiltro(nuevoFiltro) {
        if (this.tipoFiltro) {
            this.tipoFiltro.value = nuevoFiltro;
            this.filtrarTareas();
        }
    }
}

// Inicializar el gestor de filtros automáticamente
const gestorFiltro = new GestorFiltroTareas();

// Exponer la instancia globalmente para uso opcional desde otros scripts
window.gestorFiltroTareas = gestorFiltro;