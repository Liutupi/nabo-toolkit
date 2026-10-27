#include "tk_usb_console.h"
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include "driver/usb_serial_jtag.h"
#include "driver/usb_serial_jtag_vfs.h"
#include "esp_err.h"

void tk_usb_console_init(void)
{
    // The ROM-style VFS drops bytes after a 50 ms host stall. Queue replies in
    // the IDF interrupt driver so a busy Windows host does not lose whole chunks.
    usb_serial_jtag_driver_config_t config={.tx_buffer_size=2048,.rx_buffer_size=512};
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&config));
    usb_serial_jtag_vfs_use_driver();
    // Serial polling must yield when idle; UI and Bluetooth never wait for input.
    int flags=fcntl(STDIN_FILENO,F_GETFL);
    ESP_ERROR_CHECK(flags<0 || fcntl(STDIN_FILENO,F_SETFL,flags|O_NONBLOCK)<0 ? ESP_FAIL : ESP_OK);
    clearerr(stdin);
}
