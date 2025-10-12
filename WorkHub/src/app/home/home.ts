import { Component, OnInit, OnDestroy } from '@angular/core';
import { signal } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true, 
  imports: [CommonModule, RouterLink], // aggiunto CommonModule per usare *ngFor e *ngIf
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home implements OnInit, OnDestroy{
  protected readonly title = 'WorkHub';
  menuOpen = false;

  toggleMenu() {
    this.menuOpen = !this.menuOpen;
  }

  selectedLang: string = 'it'; // di default Italiano
  setLang(lang: string) {
    this.selectedLang = lang;
    console.log('Lingua selezionata:', lang);
  }

  immagini = [
    'https://i.pinimg.com/1200x/ee/e9/53/eee9535e1b135cff43a28ea56a9ef559.jpg',
    'https://i.pinimg.com/736x/65/0f/20/650f20e5f5fcc6a3149e28d180a88b5c.jpg',
    'https://i.pinimg.com/736x/6f/3f/28/6f3f2894a61e8baea6091daf75e5b13f.jpg'
  ];

    currentIndex = 0;
  private intervalId: any;

  nextSlide() {
    this.currentIndex = (this.currentIndex + 1) % this.immagini.length;
  }

  prevSlide() {
    this.currentIndex =
      (this.currentIndex - 1 + this.immagini.length) % this.immagini.length;
  }
  ngOnInit() {
    this.intervalId = setInterval(() => {
      this.nextSlide();
    }, 3000); // ogni 3 secondi
  }

  // 👇 pulizia quando il componente viene distrutto
  ngOnDestroy() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }
}