import tkinter as tk

def pantalla_principal():
    # Variable global para almacenar el valor del botón
    resultado = None

    # Funciones para los botones
    def asign_tasks():
        nonlocal resultado
        resultado = 1
        ventana.destroy()

    def view_tasks():
        nonlocal resultado
        resultado = 2
        ventana.destroy()

    def exit_tasks():
        nonlocal resultado
        resultado = 0
        ventana.destroy()

    # Crear una ventana
    ventana = tk.Tk()
    ventana.title("Gestor de tareas")

    # Crear botones
    boton1 = tk.Button(ventana, text="Crear Tarea", command=asign_tasks)
    boton2 = tk.Button(ventana, text="Ver Tareas", command=view_tasks)
    boton3 = tk.Button(ventana, text="Salir", command=exit_tasks)

    # Organizar los elementos en la ventana
    boton1.pack()
    boton2.pack()
    boton3.pack()

    # Iniciar el bucle principal de la interfaz gráfica
    ventana.mainloop()

    # Devolver el valor del botón después de que la ventana se haya cerrado
    return resultado
