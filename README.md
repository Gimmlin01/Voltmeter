# Voltmeter
LMU Voltmeter

Programm Besteht aus 3 Teilen:
main.py:
  Verantwortlich für die GUI(PyQT5).
  MainPage in der die Plots und die Aktionen dargestellt werden.
  LcdPage in der der Aktuelle Messwert angezeigt werden kann.

Connection.py:
  Eine Connection ist ein Object mit folgenden Eigenschaften:
    outQueue = eine Warteschlange in der der InputThread seine Ausgelesenen Messwerte schreibt
    inputThread = ein Thread(Prozess der nicht im main loop läuft sondern seperat) der die
                  Messungen ausliest und diese mit der dazugehörigen Zeit zu einem Messpunkt
                  verarbeitet und diesen dann schließlich in die outQueue schiebt

Plotter.py:
  Plot ist eine Klasse die ein pyqtgraph.PlotWidget ergänzt:
    data = jeweilige Messpunkte des Plots
    newData = pyqt signal(siehe pyqt signal)
    connection = siehe Connection.py
    plotThread =  ein Thread der die outQueue der derzeitigen Connection ausliest und die einzelnen
                  Messwerte dann in die data Array schreibt und den aktuellen Messwert über das
                  newData emmitiert
    updatePlot =  Funktion die falls sie an newData connected ist den Plot mit dem derzeitigem data Plottet


GUI aufbau:

MainPage:
  toolbar
  menuBar
  tabWidget:
    Tab:
      Plot

pyqt signal:
  Eine art Queue die aber dynamischer ist. Man kann an ein solches signal eine Funktion connecten die dann,
  falls das Signal emmitiert wird ausgeführt wird.


Hinzufügen neuer "Interfaces":
  im InputThread die run() Funktion abändern







All Icons made by http://www.flaticon.com/authors/freepik from www.flaticon.com
author: Michael Auer
