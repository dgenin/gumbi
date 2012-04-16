#ifndef __SOFT_SPI_H__
#define __SOFT_SPI_H__

#include <avr/io.h>
#include "common.h"
#include "mcp23s17.h"

#define SPI_READ_COMMAND 0x03

void spi_flash(void);
void spi_eeprom(void);
uint8_t validate_spi_config(void);
void soft_spi_init(void);
void soft_spi_release(void);
void spi_dump(void);
void read_spi_eeprom(void);
void read_spi_flash(void);
void soft_spi_write(uint8_t byte);
uint8_t soft_spi_read(void);

#endif