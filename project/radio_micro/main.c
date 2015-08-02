/*******************************************************/
/* ��   �ƣ�NRF24L01+����USBͨ��ģ�����               */
/* ��   �ܣ��������ݷ��ͽ��ճ���                       */
/*          ��ʽ����λ�Ǹ����������Ҫ���͵�����       */ 
/*                ���磺����5���ֽ� 11 22 33 44 55     */
/*                ���Դ��ڷ��ͣ�1122334455             */
/* ���ڲ����ʣ�9600                                    */        
/* ���ߣ�ration     ����̳��www.rationmcu.com��        */
/*                  ����ַ��ration.taobao.com��        */
/* ��ϵ��ʽ��QQ:253057617     ������qq253057617        */
/*           �ֻ���15234021671��ɽ��̫ԭ��             */
/*******************************************************/
#include<reg51.h>
#include<intrins.h>

#define uchar unsigned char
#define uint  unsigned int

/**********  NRF24L01�Ĵ�����������  ***********/
#define READ_REG        0x00  //�����üĴ���,��5λΪ�Ĵ�����ַ
#define WRITE_REG       0x20  //д���üĴ���,��5λΪ�Ĵ�����ַ
#define RD_RX_PLOAD     0x61  //��RX��Ч����,1~32�ֽ�
#define WR_TX_PLOAD     0xA0  //дTX��Ч����,1~32�ֽ�
#define FLUSH_TX        0xE1  //���TX FIFO�Ĵ���.����ģʽ����
#define FLUSH_RX        0xE2  //���RX FIFO�Ĵ���.����ģʽ����
#define REUSE_TX_PL     0xE3  //����ʹ����һ������,CEΪ��,���ݰ������Ϸ���.
#define R_RX_PL_WID		0x60
#define W_ACK_PAYLOAD	0xA8
#define NOP             0xFF  //�ղ���,����������״̬�Ĵ���	 
/**********  NRF24L01�Ĵ�����ַ   *************/
#define CONFIG          0x00  //���üĴ�����ַ                             
#define EN_AA           0x01  //ʹ���Զ�Ӧ���� 
#define EN_RXADDR       0x02  //���յ�ַ����
#define SETUP_AW        0x03  //���õ�ַ���(��������ͨ��)
#define SETUP_RETR      0x04  //�����Զ��ط�
#define RF_CH           0x05  //RFͨ��
#define RF_SETUP        0x06  //RF�Ĵ���
#define STATUS          0x07  //״̬�Ĵ���
#define OBSERVE_TX      0x08  // ���ͼ��Ĵ���
#define CD              0x09  // �ز����Ĵ���
#define RX_ADDR_P0      0x0A  // ����ͨ��0���յ�ַ
#define RX_ADDR_P1      0x0B  // ����ͨ��1���յ�ַ
#define RX_ADDR_P2      0x0C  // ����ͨ��2���յ�ַ
#define RX_ADDR_P3      0x0D  // ����ͨ��3���յ�ַ
#define RX_ADDR_P4      0x0E  // ����ͨ��4���յ�ַ
#define RX_ADDR_P5      0x0F  // ����ͨ��5���յ�ַ
#define TX_ADDR         0x10  // ���͵�ַ�Ĵ���
#define RX_PW_P0        0x11  // ��������ͨ��0��Ч���ݿ��(1~32�ֽ�) 
#define RX_PW_P1        0x12  // ��������ͨ��1��Ч���ݿ��(1~32�ֽ�) 
#define RX_PW_P2        0x13  // ��������ͨ��2��Ч���ݿ��(1~32�ֽ�) 
#define RX_PW_P3        0x14  // ��������ͨ��3��Ч���ݿ��(1~32�ֽ�) 
#define RX_PW_P4        0x15  // ��������ͨ��4��Ч���ݿ��(1~32�ֽ�)
#define RX_PW_P5        0x16  // ��������ͨ��5��Ч���ݿ��(1~32�ֽ�)
#define FIFO_STATUS     0x17  // FIFO״̬�Ĵ���
#define DYNPD			0x1C  // Dynamic payload length
#define FEATURE			0x1D  
/*����������������������������������������������������������������������������������������������������������������������������������������*/

/******   STATUS�Ĵ���bitλ����      *******/
#define MAX_TX  	0x10  //�ﵽ����ʹ����ж�
#define TX_OK   	0x20  //TX��������ж�
#define RX_OK   	0x40  //���յ������ж�
/*����������������������������������������������������������������������������������������������������*/

/*********     24L01���ͽ������ݿ�ȶ���	  ***********/
#define TX_ADR_WIDTH    5   //5�ֽڵ�ַ���
#define RX_ADR_WIDTH    5   //5�ֽڵ�ַ���
#define TX_PLOAD_WIDTH  32  //32�ֽ���Ч���ݿ��
#define RX_PLOAD_WIDTH  32  //32�ֽ���Ч���ݿ��

const uchar TX_ADDRESS[TX_ADR_WIDTH]={0x68,0x86,0x66,0x88,0x28}; //���͵�ַ
const uchar RX_ADDRESS[RX_ADR_WIDTH]={0x68,0x86,0x66,0x88,0x28}; //���͵�ַ

sbit NRF_CE = P1^5;
sbit NRF_CSN = P1^2;
sbit NRF_MISO = P3^7;
sbit NRF_MOSI = P1^0;
sbit NRF_SCK = P1^1;
sbit NRF_IRQ = P3^3;
sbit COM_LED = P3^4;

sfr AUXR = 0X8E;

uchar rece_buf[32];
uchar rece_buf2[32];
uchar tx_len = 0;
uchar *current_buf = rece_buf;
uchar *other_buf = rece_buf2;

void delay_us(uchar num)
{
	uchar i;

	for(i=0;i>num;i++)
 	_nop_();
}

void delay_150us()
{
	uint i;

	for(i=0;i>150;i++);
}

uchar SPI_RW(uchar byte)
{
	uchar bit_ctr;
	for(bit_ctr=0;bit_ctr<8;bit_ctr++) // ���8λ
	{
		NRF_MOSI=(byte&0x80); // MSB TO MOSI
		byte=(byte<<1);	// shift next bit to MSB
		NRF_SCK=1;
		byte|=NRF_MISO;	        // capture current MISO bit
		NRF_SCK=0;
	}
	return byte;
}

/*********************************************/
/* �������ܣ���24L01�ļĴ���дֵ��һ���ֽڣ� */
/* ��ڲ�����reg   Ҫд�ļĴ�����ַ          */
/*           value ���Ĵ���д��ֵ            */
/* ���ڲ�����status ״ֵ̬                   */
/*********************************************/
uchar NRF24L01_Write_Reg(uchar reg,uchar value)
{
	uchar status;

	NRF_CSN=0;                  //CSN=0;   
  	status = SPI_RW(reg);//���ͼĴ�����ַ,����ȡ״ֵ̬
	SPI_RW(value);
	NRF_CSN=1;                  //CSN=1;

	return status;
}
/*************************************************/
/* �������ܣ���24L01�ļĴ���ֵ ��һ���ֽڣ�      */
/* ��ڲ�����reg  Ҫ���ļĴ�����ַ               */
/* ���ڲ�����value �����Ĵ�����ֵ                */
/*************************************************/
uchar NRF24L01_Read_Reg(uchar reg)
{
 	uchar value;

	NRF_CSN=0;              //CSN=0;   
  	SPI_RW(reg);//���ͼĴ���ֵ(λ��),����ȡ״ֵ̬
	value = SPI_RW(NOP);
	NRF_CSN=1;             //CSN=1;

	return value;
}
/*********************************************/
/* �������ܣ���24L01�ļĴ���ֵ������ֽڣ�   */
/* ��ڲ�����reg   �Ĵ�����ַ                */
/*           *pBuf �����Ĵ���ֵ�Ĵ������    */
/*           len   �����ֽڳ���              */
/* ���ڲ�����status ״ֵ̬                   */
/*********************************************/
uchar NRF24L01_Read_Buf(uchar reg,uchar *pBuf,uchar len)
{
	uchar status,u8_ctr;
	NRF_CSN=0;                   //CSN=0       
  	status=SPI_RW(reg);//���ͼĴ�����ַ,����ȡ״ֵ̬   	   
 	for(u8_ctr=0;u8_ctr<len;u8_ctr++)
	pBuf[u8_ctr]=SPI_RW(0XFF);//��������
	NRF_CSN=1;                 //CSN=1
  	return status;        //���ض�����״ֵ̬
}
/**********************************************/
/* �������ܣ���24L01�ļĴ���дֵ������ֽڣ�  */
/* ��ڲ�����reg  Ҫд�ļĴ�����ַ            */
/*           *pBuf ֵ�Ĵ������               */
/*           len   �����ֽڳ���               */
/**********************************************/
uchar NRF24L01_Write_Buf(uchar reg, uchar *pBuf, uchar len)
{
	uchar status,u8_ctr;
	NRF_CSN=0;
  	status = SPI_RW(reg);//���ͼĴ���ֵ(λ��),����ȡ״ֵ̬
  	for(u8_ctr=0; u8_ctr<len; u8_ctr++)
	SPI_RW(*pBuf++); //д������
	NRF_CSN=1;
  	return status;          //���ض�����״ֵ̬
}							  					   

/*********************************************/
/* �������ܣ�24L01��������                   */
/* ��ڲ�����rxbuf ������������              */
/* ����ֵ�� �յ������ݳ���                   */
/*          0   û���յ�����                 */
/*********************************************/
uchar NRF24L01_RxPacket(uchar *rxbuf, uchar *again, uchar *len)
{
	uchar state;
	uchar morePayload;

	if (!(*again)) {
		state=NRF24L01_Read_Reg(STATUS);  //��ȡ״̬�Ĵ�����ֵ    	 
		NRF24L01_Write_Reg(WRITE_REG+STATUS,state); //���TX_DS��MAX_RT�жϱ�־
	}

	if((*again) || state&RX_OK)//���յ�����
	{
		NRF_CE = 0;
		NRF24L01_Read_Buf(R_RX_PL_WID, len, 1); // Read the length of the packet
		NRF24L01_Read_Buf(RD_RX_PLOAD,rxbuf,*len);//��ȡ����
//		NRF24L01_Write_Reg(FLUSH_RX,0xff);//���RX FIFO�Ĵ���
		morePayload = NRF24L01_Read_Reg(FIFO_STATUS);
		NRF_CE = 1;
		delay_150us(); 
		if (morePayload & 0x01)	{
			*again = 0;
			return 0; 
		}
		else {
			*again = 1;
			return 2; // �и������ݵȴ���ȡ����Ҫ�ٴζ�FIFO�Ĵ���
		}
	}	   
	return 1;//û�յ��κ�����
}
/**********************************************/
/* �������ܣ�����24L01Ϊ����ģʽ              */
/* ��ڲ�����txbuf  ������������              */
/* ����ֵ�� 0x10    �ﵽ����ط�����������ʧ��*/
/*          0x20    �ɹ��������              */
/*          0xff    ����ʧ��                  */
/**********************************************/
uchar NRF24L01_TxPacket(uchar *txbuf)
{
	uchar state;
   
	NRF_CE=0;//CE���ͣ�ʹ��24L01����
  	NRF24L01_Write_Buf(WR_TX_PLOAD,txbuf,TX_PLOAD_WIDTH);//д���ݵ�TX BUF  32���ֽ�
 	NRF_CE=1;//CE�øߣ�ʹ�ܷ���	   
	while(NRF_IRQ==1);//�ȴ��������
	state=NRF24L01_Read_Reg(STATUS);  //��ȡ״̬�Ĵ�����ֵ	   
	NRF24L01_Write_Reg(WRITE_REG+STATUS,state); //���TX_DS��MAX_RT�жϱ�־
	if(state&MAX_TX)//�ﵽ����ط�����
	{
		NRF24L01_Write_Reg(FLUSH_TX,0xff);//���TX FIFO�Ĵ��� 
		return MAX_TX; 
	}
	if(state&TX_OK)//�������
	{
		return TX_OK;
	}
	return 0xff;//����ʧ��
}

/********************************************/
/* �������ܣ����24L01�Ƿ����              */
/* ����ֵ��  0  ����                        */
/*           1  ������                      */
/********************************************/ 	  
uchar NRF24L01_Check(void)
{
	uchar check_in_buf[5]={0x11,0x22,0x33,0x44,0x55};
	uchar check_out_buf[5]={0x00};

	NRF_SCK=0;
	NRF_CSN=1;    
	NRF_CE=0;

	NRF24L01_Write_Buf(WRITE_REG+TX_ADDR, check_in_buf, 5);

	NRF24L01_Read_Buf(READ_REG+TX_ADDR, check_out_buf, 5);

	if((check_out_buf[0] == 0x11)&&\
	   (check_out_buf[1] == 0x22)&&\
	   (check_out_buf[2] == 0x33)&&\
	   (check_out_buf[3] == 0x44)&&\
	   (check_out_buf[4] == 0x55))return 0;
	else return 1;
}			

/******************************************************************/
/* �򿪴��� ��ʹ�ö�ʱ��1��Ϊ�����ʷ�������������115200           */
/******************************************************************/
// NOTE: When flashing using the STC_ISR tool, make sure to select "Use external clock"!!
// The default is always "Use internal RC clock", which will screw up the baud rate!!
void serial_open(void)
{
	AUXR |= (1<<6);     // ���ö�ʱ��1Ϊ1Tģʽ
	TMOD = 0x20;				// ��ʱ��T1ʹ�ù�����ʽ2,8λ�Զ�����
	SCON = 0x50;				// SM0=0 SM1=1 SM2=0 REN=1 TB8=0 RB8=0 TI=0 RI=0
	TH1 = 0xFD;					// 9600	(���11.0592M����)
	TL1 = 0xFD;
	PCON = 0x80;				// SMOD =1    ��Ƶ
	TR1 = 1;					// ��ʼ��ʱ
}
	  
bit WaitComm(uchar *len)
{	 
	uint i=0;
	uchar j=0;
		
	if(RI)
    {
		rece_buf[j++]=SBUF;	  //���յ������ݷ��뻺����recebuf��
		RI=0;
		while(i<500) 
		{
		  	if(RI)
			{
			   	rece_buf[j++]=SBUF;
				RI = 0;
				i=0;
				if (j >= 32) break;	
			}
			i++;
		}
		*len = j;		
		return 0;		  //�����ݽ��յ�������0
	}
	else
	{
		return 1;		  //�����ݽ��յ�������1
	}
}



/******************�������ݺ���********************/

void NRF24L01_RT_Init(void)
{	
	NRF_CE=0;		  
//  	NRF24L01_Write_Reg(WRITE_REG+RX_PW_P0,RX_PLOAD_WIDTH);//ѡ��ͨ��0����Ч���ݿ��
	NRF24L01_Write_Reg(WRITE_REG+FEATURE,0x06); // Enable DPL
	NRF24L01_Write_Reg(WRITE_REG+0x1C,0x01); // Set DPL_P0
	NRF24L01_Write_Reg(FLUSH_RX,0xff);//���RX FIFO�Ĵ���    
//  	NRF24L01_Write_Buf(WRITE_REG+TX_ADDR,(uchar*)TX_ADDRESS,TX_ADR_WIDTH);//дTX�ڵ��ַ 
  	NRF24L01_Write_Buf(WRITE_REG+RX_ADDR_P0,(uchar*)RX_ADDRESS,RX_ADR_WIDTH); //����TX�ڵ��ַ,��ҪΪ��ʹ��ACK	  
  	NRF24L01_Write_Reg(WRITE_REG+EN_AA,0x01);     //ʹ��ͨ��0���Զ�Ӧ��    
  	NRF24L01_Write_Reg(WRITE_REG+EN_RXADDR,0x01); //ʹ��ͨ��0�Ľ��յ�ַ  
//  	NRF24L01_Write_Reg(WRITE_REG+SETUP_RETR,0x1a);//�����Զ��ط����ʱ��:500us + 86us;����Զ��ط�����:10��
  	NRF24L01_Write_Reg(WRITE_REG+RF_CH,40);       //����RFͨ��Ϊ40
  	NRF24L01_Write_Reg(WRITE_REG+RF_SETUP,0x26);  //����TX�������,0db����,250kbps,���������濪��   
  	NRF24L01_Write_Reg(WRITE_REG+CONFIG,0x0f);    //���û�������ģʽ�Ĳ���;PWR_UP,EN_CRC,16BIT_CRC,����ģʽ,���������ж�
	NRF_CE=1;	//CE�øߣ�ʹ�ܷ���
}


void main()
{
	uchar i=0;
	uchar len=0;
	uchar readAgain = 0;
	uchar *ptr;
	COM_LED = 0;
 	serial_open();
	while(NRF24L01_Check()); // �ȴ���⵽NRF24L01������Ż�����ִ��
	NRF24L01_RT_Init();
    COM_LED = 1;

	// Enable serial interrupt to handle RX
	ES = 1;
	EA = 1;

	while(1)
	{
		if(NRF_IRQ==0)	 // �������ģ����յ�����
		{
			len = 0;
			readAgain = 0;
			while(NRF24L01_RxPacket(other_buf, &readAgain, &len) != 1)
			{
				COM_LED = !COM_LED;
				
			    if (len > 32) {
					break;
				}

				for (i = 0; i < len; i++)
				{
					TI = 0;	
					SBUF = other_buf[i];
					while(!TI);
				}
				TI = 0;
				
				if (readAgain == 0) break;
				len = 0;
			}

			// Upload ACK payload
		 	if(tx_len > 0) {
				// Switch to the other rece_buf in a critical section
				EA = 0;
				ptr = current_buf;
				len = tx_len;
				if (current_buf == rece_buf) {
					current_buf = rece_buf2;
					other_buf = rece_buf;
				} else {
					current_buf = rece_buf;
					other_buf = rece_buf2;
				}
				tx_len = 0;
				EA = 1;

				// We've got data from the PC. Put the data as ACK payload
				// into the TX FIFO.
				// Note: Flow control should be done by the PC. Basically, the PC
				// should only send out a new packet per packet it receives.
				NRF24L01_Write_Buf(W_ACK_PAYLOAD, ptr, len);
			}
		}

		/*
		if(WaitComm()==0)	 // ����ӵ��Դ��ڷ�������
		{
			NRF_CE=0;
			NRF24L01_Write_Reg(WRITE_REG+CONFIG,0x0e);
			NRF_CE=1;
			delay_us(15);
			NRF24L01_TxPacket(rece_buf);
			NRF_CE=0;
			NRF24L01_Write_Reg(WRITE_REG+CONFIG, 0x0f);
			NRF_CE=1;
		}
		*/
	}
}

void SerialISR(void) interrupt 4
{
	if(RI) {
		RI = 0;
		current_buf[tx_len++] = SBUF;
		if (tx_len >= 31) {
			tx_len = 31;
		}
	}
}

