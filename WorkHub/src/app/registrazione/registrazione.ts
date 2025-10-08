import { Component, OnInit, OnDestroy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormArray, FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';

@Component({
  selector: 'app-registrazione',
  imports: [RouterLink],
  templateUrl: './registrazione.html',
  styleUrls: ['./registrazione.css']
})
export class Registrazione {
 ngOnInit(): void {
    // Blocca lo scroll
    document.body.style.overflow = 'hidden';
  }

  ngOnDestroy(): void {
    // Ripristina lo scroll quando esci dal componente
    document.body.style.overflow = 'auto';
  }
}
