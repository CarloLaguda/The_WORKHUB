import { Component } from '@angular/core';
import { signal } from '@angular/core';

@Component({
  selector: 'app-home',
  imports: [],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home {
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
