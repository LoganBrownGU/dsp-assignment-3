#ifndef UART_H
#define UART_H


class UART {
private:
    unsigned char buf[8];
    

public: 
    unsigned char *getByte();

};

#endif