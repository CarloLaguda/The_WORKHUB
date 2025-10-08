import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Prova } from './prova';

describe('Prova', () => {
  let component: Prova;
  let fixture: ComponentFixture<Prova>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Prova]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Prova);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
