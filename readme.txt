Cómo utilizar:

Requisitos:

La biblioteca ibex-lib instalada y construida.
Python 3 instalado, junto con la biblioteca Pandas.

Instrucciones:

Modifica el script para establecer las rutas correctas para tu entorno:

	base_dir: Esta es la carpeta base donde se encuentran tus carpetas ibex-lib e ibex-tools.

	ibex_dir: Esta es la carpeta donde se encuentra ibex-lib.

	tools_dir: Esta es la carpeta donde se encuentran ibex-tools y tus archivos de salida.

	python_interpreter: Esta es la ubicación de tu intérprete de Python 3. (Ejecutar "where python3")

	python_script: Esta es la ubicación del script de Python para analizar los resultados.

	input_file: archivo de texto que contiene la lista de benchmarks a ejecutar. Cada línea en el archivo debe contener una ruta relativa al directorio ibex_dir y terminar con el nombre del benchmark.

	num_runs: número de veces que deseas ejecutar cada benchmark.

	max_jobs: cantidad de ejecuciones en paralelo. Por defecto igual al numero de nucleos de CPU disponibles en la maquina.



Comando para ejecutar: "sudo -E ./run_tests.sh"


Ejecuta el script en tu shell de Bash. El script imprimirá su progreso en la consola y creará archivos de salida para cada ejecución de benchmark en el directorio outputs de tu tools_dir.

Después de que se hayan completado todas las ejecuciones, el script llamará al script de Python especificado para analizar los archivos de salida y combinar los resultados en un solo archivo CSV.

Recuerda hacer que el script sea ejecutable (chmod +x run_tests.sh) antes de ejecutarlo.







