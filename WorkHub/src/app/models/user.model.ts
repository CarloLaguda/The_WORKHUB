export interface User { //MODELLO PER USER GENERALE
    anni_di_esperienza: number;
    country: string;
    email: string;
    eta: number;
    first_name: string;
    gender: 'M' | 'F' | string; 
    last_name: string;
    skills: string | null;
    status: 'libero' | 'occupato' | string;
    user_id: number;
    username: string;
    password: string //Criptata
}