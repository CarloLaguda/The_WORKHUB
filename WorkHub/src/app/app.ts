import { signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('WorkHub');
  menuOpen = false;

  toggleMenu() {
    this.menuOpen = !this.menuOpen;
  }
  selectedLang: string = 'it'; // di default Italiano

  setLang(lang: string) {
    this.selectedLang = lang;
    console.log('Lingua selezionata:', lang);
    // qui puoi aggiungere logica per traduzioni / i18n
    }
}
