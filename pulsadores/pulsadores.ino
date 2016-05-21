// entradas de los pulsadores
const int botonRojo = 2;
const int botonBlanco = 4;
const int botonReset = 5;
const int botonNext = 6;
const int botonPlata = 3;
const int botonAzul = 7;
const int botonAmarillo = 10;

const int electroiman_PWM = 11;

// contadores de cuantas veces se ha pulsado tal pulsador
int rojoCounter = 0;
int blancoCounter = 0;
int plataCounter = 0;
int amarilloCounter = 0;
int azulCounter = 0;
int nextCounter = 0;

char respuesta50[3];
char respuesta51[9];

void setup() {
  pinMode(botonRojo,INPUT);
  pinMode(botonAmarillo,INPUT);
  pinMode(botonAzul,INPUT);
  pinMode(botonPlata,INPUT);
  pinMode(botonBlanco,INPUT);
  pinMode(botonNext,INPUT);
  pinMode(botonReset,INPUT);
  // comenzamos una comunicacion con el arduino
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    byte resp = Serial.read();
    if(resp==49){
      analogWrite(electroiman_PWM,255);
    }
    else if (resp==48) {
      analogWrite(electroiman_PWM,0);
    }
    else if (resp==50) {
      //interaccion 4 pulsadores
      while(nextCounter<2) {
        //interaccion 4 pulsadores
        if (digitalRead(botonRojo) == LOW) {
          rojoCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonBlanco) == LOW) {
          blancoCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonNext) == LOW) {
          nextCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonReset) == LOW) {
          rojoCounter = 0;
          blancoCounter = 0;
          nextCounter = 0;
          delay(500);
        }
      }
      if (nextCounter == 2) {
        sprintf(respuesta50, "%d|%d", rojoCounter, blancoCounter);
        rojoCounter = 0;
        blancoCounter = 0;
        nextCounter = 0;
        Serial.write(respuesta50);
      }
    }
    else if (resp==51) {
      while(nextCounter<5) {
        //interaccion 7 pulsadores
        if (digitalRead(botonRojo) == LOW) {
          rojoCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonBlanco) == LOW) {
          blancoCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonAmarillo) == LOW) {
          amarilloCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonPlata) == LOW) {
          plataCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonAzul) == LOW) {
          azulCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonNext) == LOW) {
          nextCounter += 1;
          delay(500);
        }
        else if (digitalRead(botonReset) == LOW) {
          rojoCounter = 0;
          blancoCounter = 0;
          plataCounter = 0;
          amarilloCounter = 0;
          azulCounter = 0;
          nextCounter = 0;
          delay(500);
        }
      }
      if (nextCounter == 5) {
        sprintf(respuesta51, "%d|%d|%d|%d|%d", rojoCounter, azulCounter, amarilloCounter, blancoCounter, plataCounter);
        rojoCounter = 0;
        blancoCounter = 0;
        plataCounter = 0;
        amarilloCounter = 0;
        azulCounter = 0;
        nextCounter = 0;
        Serial.write(respuesta51);
      }
    }
  }
}

