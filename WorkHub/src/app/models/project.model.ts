export class Project {//Modello di dtai per i progetti
  constructor(
    public project_id: number,
    public title: string,
    public description: string,
    public availability: string,
    public max_persone: number,
    public is_full: number,
    public creator_name: string,
    public required_skills: string,
    public environments: string,  
    public user_count: number
  ) {}
}
