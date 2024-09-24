using System;

namespace Projekt1
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string[] gültigeWahlen = { "1", "2", "3" };
            while (true)
            {
                Console.WriteLine("1. für Name 2. für Rechner 3. für Beenden");
                string wahl = Console.ReadLine();

                if (wahl == "1")
                {
                    AbfrageName();
                }
                else if (wahl == "2")
                {
                    Rechner();
                }
                else if (wahl == "3")
                {
                    break;
                }
                else if (!Array.Exists(gültigeWahlen, element => element == wahl))
                {
                    Console.WriteLine("Ungültige Wahl. Bitte entweder 1, 2 oder 3 eingeben.");
                }
            }
        }

        static void AbfrageName()
        {
            while (true)
            {
                Console.Write("Wie ist dein Vorname: ");
                string vorname = Console.ReadLine();
                Console.Write("Wie ist dein Nachname: ");
                string nachname = Console.ReadLine();

                if (!IstEingabeGültig(vorname) || !IstEingabeGültig(nachname))
                {
                    Console.WriteLine("Ungültige Eingabe. Bitte keine Zahlen oder leere Felder eingeben.");
                    continue;
                }

                int alter = AbfrageAlter();
                if (alter != -1)
                {
                    Console.WriteLine($"Hallo {vorname} {nachname}, du bist {alter} Jahre alt.");
                    Console.WriteLine("Drücke eine Taste zum Fortfahren...");
                    Console.ReadKey(true);
                    break;
                }
            }
        }

        static int AbfrageAlter()
        {
            while (true)
            {
                Console.Write("Wie alt bist du: ");
                string alter = Console.ReadLine();

                if (int.TryParse(alter, out int alterInt))
                {
                    return alterInt;
                }
                else
                {
                    Console.WriteLine($"Ungültige Eingabe: '{alter}' ist keine Zahl. Bitte erneut versuchen.");
                }
            }
        }

        static bool IstEingabeGültig(string eingabe)
        {
            return !string.IsNullOrWhiteSpace(eingabe) && !int.TryParse(eingabe, out _);
        }

        static void Rechner()
        {
            Console.WriteLine("Rechnerfunktion kommt hier hin...");
            Console.ReadKey(true);
        }
    }
}
