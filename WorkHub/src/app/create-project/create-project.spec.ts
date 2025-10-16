import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateProject } from './create-project';

describe('CreateProject', () => {
  let component: CreateProject;
  let fixture: ComponentFixture<CreateProject>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateProject]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateProject);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
