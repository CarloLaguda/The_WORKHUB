import { Component, Input } from '@angular/core';
import { Project } from '../models/project.model';

@Component({
  selector: 'app-prova',
  imports: [],
  templateUrl: './prova.html',
  styleUrl: './prova.css'
})
export class Prova {
  @Input() progetto!: Project

}
