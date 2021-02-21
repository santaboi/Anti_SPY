#include "embARC.h"
#include "embARC_debug.h"

#define GPIO4B2_1_OFFSET	1
#define GPIO4B2_3_OFFSET	3

void t1_isr(void *ptr)  //use Timer to make the LED blink
{
    // Clear IP first
    timer_int_clear(TIMER_1);

    uint32_t read_value;
DEV_GPIO_PTR gpio_4b2 = gpio_get_dev(DFSS_GPIO_4B2_ID);
    gpio_4b2->gpio_read(&read_value, 1<<GPIO4B2_3_OFFSET);
    gpio_4b2->gpio_write(~read_value, 1<<GPIO4B2_3_OFFSET);
}

int main(void)
{
    // get 4b2 gpio object
    DEV_GPIO_PTR gpio_4b2 = gpio_get_dev(DFSS_GPIO_4B2_ID);
    /*
      Open GPIO
      input   : 0, 1, 2
      output  : 3
    */
    gpio_4b2->gpio_open(1<<GPIO4B2_3_OFFSET);
    uint32_t read_value = 0;
    
    DEV_UART_PTR uart_1 = uart_get_dev(DFSS_UART_1_ID);
    uart_1->uart_open(9600);
    uint8_t read_value_blue = 0;
    //偵測按鈕是否被按
    while(1)
    {
        gpio_4b2->gpio_read(&read_value, 1<<GPIO4B2_1_OFFSET);
        //偵測到按鈕被按
        if(read_value>>1 == 1)
        {
            uart_1->uart_write("b", 1);  //透過按鈕發送"b"到處理人臉辨識的電腦以啟動裝置
            board_delay_ms(1000, 0);
            break;
        }
    }
    read_value = 0;  //reset read_value值以進行下一輪按鈕偵測
    
    while(1)
    {
        //裝置還沒收到來自另一台電腦的訊號'a'
        while(read_value_blue != 'a')
        {
            uart_1->uart_read(&read_value_blue, 1);  //透過藍芽接收訊號
            EMBARC_PRINTF("a:%c\n", read_value_blue); //test
        }

        //裝置透過藍芽接收到來自另一台電腦的訊號'a'並且讓LED燈開始閃以通知使用者

        // Reset TIMER1
        // Check whether TIMER1 is available before use it
        if(timer_present(TIMER_1))
        {
            // Stop TIMER1 & Disable its interrupt first
            timer_stop(TIMER_1);
            int_disable(INTNO_TIMER1);

            // Connect a ISR to TIMER1's interrupt
            int_handler_install(INTNO_TIMER1, t1_isr);

            // Enable TIMER1's interrupt
            int_enable(INTNO_TIMER1);
            
            // Start counting, 1 second request an interrupt
            timer_start(TIMER_1, TIMER_CTRL_IE, BOARD_CPU_CLOCK);
        }

        //偵測使用者是否透過按鈕對於閃燈作出回應
        while(1)
        {
            gpio_4b2->gpio_read(&read_value, 1<<GPIO4B2_1_OFFSET);
            //使用者按下按鈕，關閉裝置並且傳送"c"到另一台電腦促使其關機
            if(read_value>>1 == 1)
            {
                uart_1->uart_write("c", 1);
                board_delay_ms(1000,0);  //若沒有delay會導致訊號無法送達
                gpio_4b2->gpio_write(0<<GPIO4B2_3_OFFSET, 1<<GPIO4B2_3_OFFSET);  //關燈
                break;
            }
        }        
        break;
    }
    
    gpio_4b2->gpio_close();
    uart_1->uart_close();

    return E_SYS;
}
