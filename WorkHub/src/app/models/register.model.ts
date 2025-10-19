export class Register{ //Modello di dati per la registrazione base
    constructor(
        public username: string,
        public email: string,
        public password: string,
        public first_name: string,
        public last_name: string,
        public eta: number,
        public gender: string
    ){}
}