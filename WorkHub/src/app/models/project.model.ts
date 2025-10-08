export class Project { // MODELLO PER IL PROGETTO BASE, DA AGGIUNGERE DETTAGLI
  constructor(
    public availability: string,
    public description: string,
    public project_id: string,
    public is_full: number,
    public max_persone: number,
    public title: string
  ) {}
}
