#include <stdio.h>
#include <stdbool.h>
#include "windows.h"
#include "debug.h"
#include "types.h"
#include "alloc-inl.h"
#include "winaflt32.h"
//#include <winsock.h>
static unsigned char *trace_buffer;
static HANDLE child_handle;
static uint64_t dbg_timeout_time = 0;
static int fuzz_iterations_current;
CRITICAL_SECTION critical_section;

HANDLE hCtrlPipe = INVALID_HANDLE_VALUE;
HANDLE hDataPipe = INVALID_HANDLE_VALUE;

LPCTSTR PIPE_CTRL = TEXT("\\\\.\\pipe\\CmdPipe");
LPCTSTR PIPE_DATA = TEXT("\\\\.\\pipe\\DataPipe");

u64 get_cur_time(void);
#define  TRACE_TIMEOUT_MSEC 30*1000 //30 seconds

static uint64_t trace_timeout_time;


static FILE *debug_log = NULL;
#define LOG(fmt, ...) printf(("%s(%d)\t" fmt "\n"), __FUNCTION__, __LINE__, ##__VA_ARGS__)
#define LOG_FILE(fmt, ...) if(debug_log){ \
						fprintf(debug_log,("[AFL]%s(%d)\t" fmt ""), __FUNCTION__, __LINE__, ##__VA_ARGS__); \
						fflush(debug_log); \
						}

enum {
	/* 00 */ FAULT_NONE,
	/* 01 */ FAULT_TMOUT,
	/* 02 */ FAULT_CRASH,
	/* 03 */ FAULT_ERROR,
	/* 04 */ FAULT_NOINST,
	/* 05 */ FAULT_NOBITS
};



#define CtrlBUFSIZE 512
#define DataBUFSIZE 65536

#define COVERAGE_BB 0


#define CMD_INIT 0xdead1001
#define CMD_GO 0xdead1002
#define CMD_SUSPEND 0xdead1002



#define STATUS_READY 0xbeef0221
#define STATUS_SUSPEND 0xbeef0222
#define STATUS_LOOP1DONE 0xbeef0223
#define STATUS_ERROR 0xbeef022f




char *getPrintMsg(int msgid){

	switch (msgid)
	{
	case STATUS_READY:
		/* code */
		return "STATUS_READY";
	case STATUS_SUSPEND:
		/* code */
		return "STATUS_SUSPEND";

	case STATUS_LOOP1DONE:
	/* code */
	return "STATUS_LOOP1DONE";
	case STATUS_ERROR:
	/* code */
	return "STATUS_ERROR";
	default:
		return "UNKNOWN MSG";;
	}


}



#define ntohl(A)  ((((UINT32)(A) & 0xff000000) >> 24) | \
                            (((UINT32)(A) & 0x00ff0000) >> 8) | \
                            (((UINT32)(A) & 0x0000ff00) << 8) | \
                            (((UINT32)(A) & 0x000000ff) << 24))

typedef struct _winafl_option_t {
	bool debug_mode;
	int coverage_kind;
	//module_info_t *coverage_modules;
	char fuzz_module[MAX_PATH];
	char fuzz_method[MAX_PATH];
	unsigned long fuzz_offset;
	int fuzz_iterations;
	int num_fuz_args;
	//int callconv;
	int decoder;
	bool thread_coverage;
	unsigned long trace_buffer_size;
	unsigned long trace_cache_size;
	bool persistent_trace;

	void **func_args;
	void *sp;
	void *fuzz_address;
} winafl_option_t;
static winafl_option_t options;

int winaflt32_options_init()
{
	int i;
	const char *token;
	/* default values */
	options.debug_mode = false;
	options.coverage_kind = COVERAGE_BB;
	printf("Debug: winaflt32_options_init\n");
	options.trace_cache_size = 0;
	options.persistent_trace = true;

	debug_log = fopen("t32debug.log", "w");
	if (!debug_log) {
		FATAL("Can't open debug log for writing");
	}


	return 0;

}


//init t32, include init ETM range, trace method..
int t32_init( char **argv) {
	int lastoption = -1;

	winaflt32_options_init();
	LOG_FILE("Debug: t32_init\n");

	return lastoption;
}



DWORD WINAPI  t32_main(char *cmd){
LOG_FILE("Debug: t32_main\n");
}

int initSharedPipe()
{
	BOOL   fConnected = FALSE; 
	hCtrlPipe = CreateNamedPipe( 
          PIPE_CTRL,             // pipe name 
          PIPE_ACCESS_DUPLEX,       // read/write access 
          PIPE_TYPE_BYTE |       // BYTE type pipe 
          PIPE_READMODE_BYTE |   // BYTE-read mode 
          PIPE_NOWAIT,                // non-blocking mode 
          PIPE_UNLIMITED_INSTANCES, // max. instances  
          CtrlBUFSIZE,                  // output buffer size 
          CtrlBUFSIZE,                  // input buffer size 
          0,                        // client time-out 
          NULL);                    // default security attribute 
	LOG_FILE("Debug: initSharedPipe\n");
	if (hCtrlPipe == INVALID_HANDLE_VALUE) 
    {
        LOG_FILE(TEXT("CreateNamedPipe failed, GLE=%d.\n"), GetLastError()); 
        return -1;
    }



	hDataPipe = CreateNamedPipe( 
          PIPE_DATA,             // pipe name 
          PIPE_ACCESS_DUPLEX,       // read/write access 
          PIPE_TYPE_BYTE |       // BYTE type pipe 
          PIPE_READMODE_BYTE |   // BYTE-read mode 
          PIPE_NOWAIT,                // non-blocking mode 
          PIPE_UNLIMITED_INSTANCES, // max. instances  
          DataBUFSIZE,                  // output buffer size 
          DataBUFSIZE,                  // input buffer size 
          0,                        // client time-out 
          NULL);                    // default security attribute 
	if (hDataPipe == INVALID_HANDLE_VALUE) 
    {
        LOG_FILE(TEXT("CreateNamedPipe failed, GLE=%d.\n"), GetLastError()); 
        return -1;
    }
	LOG_FILE(TEXT("CreateNamedPipe sucess, wait for clien...\n")); 
	Sleep(1000);

	fConnected = ConnectNamedPipe(hCtrlPipe, NULL) ? 
	TRUE : (GetLastError() == ERROR_PIPE_CONNECTED); 

	if (fConnected)
	{
		LOG_FILE(TEXT("ConnectNamedPipe hCtrlPipe sucess...\n")); 
	}
	


	fConnected = ConnectNamedPipe(hDataPipe, NULL) ? 
	TRUE : (GetLastError() == ERROR_PIPE_CONNECTED);
	if (fConnected)
	{
		LOG_FILE(TEXT("ConnectNamedPipe hDataPipe sucess...\n")); 
	}
}


static void setup_t32_main(char *cmd) {
	//InitializeCriticalSection(&critical_section);
	// CreateThread(NULL, 0, t32_main, (LPVOID)cmd, 0, &dwThreadId);
	
	STARTUPINFOA si;
	PROCESS_INFORMATION pi;
	HANDLE hJob = NULL;
	JOBOBJECT_EXTENDED_LIMIT_INFORMATION job_limit;

	LOG_FILE("Debug: setup_t32_main 111\n");

	ZeroMemory(&si, sizeof(si));
	si.cb = sizeof(si);
	ZeroMemory(&pi, sizeof(pi));
	
	si.cb = sizeof(si);
   	si.hStdOutput = debug_log ? (HANDLE)_get_osfhandle(_fileno( debug_log )):GetStdHandle(STD_OUTPUT_HANDLE);
   	si.hStdError = debug_log ? (HANDLE)_get_osfhandle(_fileno( debug_log )):GetStdHandle(STD_ERROR_HANDLE);
   	si.dwFlags |= STARTF_USESTDHANDLES;

	if (!CreateProcessA(NULL, cmd, NULL, NULL, TRUE, NULL, NULL, NULL, &si, &pi)) {
		FATAL("CreateProcess failed, GLE=%d.\n", GetLastError());
	}
	LOG_FILE("Debug: setup_t32_main 2222\n");
	child_handle = pi.hProcess;
	// child_thread_handle = pi.hThread;
	// child_entrypoint_reached = false;

	initSharedPipe();
	BOOL wow64current, wow64remote;
	if (!IsWow64Process(child_handle, &wow64remote)) {
		FATAL("IsWow64Process failed");
	}



}

int waitfor_status(int wantted){
	int status = -1;
	DWORD cbBytesRead = 0;
	BOOL fSuccess = FALSE;
	LOG_FILE("Debug: waitint for target status 0x%x\n",wantted);


	while (1) {


		fSuccess = ReadFile( 
			hCtrlPipe,        // handle to pipe 
			&status,    // buffer to receive data 
			4, // size of buffer 
			&cbBytesRead, // number of bytes read 
			NULL);        // not overlapped I/O

		if (fSuccess == 0 || cbBytesRead == 0)
		{ 
			LOG_FILE("waitfor_status: %s, try again, %d\n",getPrintMsg(wantted), GetLastError());
			Sleep(10);
			continue;
		}else{
			LOG_FILE("waitfor_status Error:%s %d\n", getPrintMsg(ntohl(status)), cbBytesRead);
			return ntohl(status);
		}
		
	}


	return status;
}

BOOL send_cmd(int cmd){
	BOOL fSuccess = FALSE;
	char cmdbuf[4] = {0};
	//HANDLE hHeap      = GetProcessHeap();
	DWORD cbBytesRead = 0, cbReplyBytes = 0, cbWritten = 0; 
    // TCHAR* pchRequest = (TCHAR*)HeapAlloc(hHeap, 0, BUFSIZE*sizeof(TCHAR));
    // TCHAR* pchReply   = (TCHAR*)HeapAlloc(hHeap, 0, BUFSIZE*sizeof(TCHAR));
	//memcpy(cmdbuf, &cmd, 4);
	int cmd_in = ntohl(cmd);
	LOG_FILE("Debug: send_cmd %x\n", cmd_in);
	fSuccess = WriteFile( 
		hCtrlPipe,        // handle to pipe 
		&cmd_in,     // buffer to write from 
		4, // number of bytes to write 
		&cbWritten,   // number of bytes written 
		NULL);        // not overlapped I/O 
	return fSuccess;
}
uint32_t get_etm_count(){

	int count = -1;
	DWORD cbBytesRead = 0;
	BOOL fSuccess = FALSE;
	//LOG_FILE("Debug: get_etm_count\n");


	while (1) {


		fSuccess = ReadFile( 
			hCtrlPipe,        // handle to pipe 
			&count,    // buffer to receive data 
			4, // size of buffer 
			&cbBytesRead, // number of bytes read 
			NULL);        // not overlapped I/O

		if (fSuccess == 0 || cbBytesRead == 0)
		{ 
			//LOG_FILE("get_etm_count try again, %d\n",GetLastError());
			Sleep(10);
			continue;
		}else{
			LOG_FILE("Debug: get_etm_count:%x %d\n", ntohl(count), cbBytesRead);
			return ntohl(count);
		}
		
	}

	return count;
}

extern u8 *trace_bits;
void update_coverage_map(char* map, uint32_t size ){
	uint32_t offset;
	uint32_t *addr = (uint32_t *)map;
	int j = 0;
	for (size_t i = 0; i < size/4; i++)
	{
		if (addr[i] != 0)
		{
				//LOG_FILE("update_coverage_map read %x\n",addr[i] );
				offset = (uint32_t)(addr[i]);
				trace_bits[offset % MAP_SIZE]++;

		}		
	}
}
TCHAR* getEtmData()
{
	BOOL fSuccess = FALSE;
	char cmdbuf[4] = {0};
	HANDLE hHeap      = GetProcessHeap();
	DWORD cbBytesRead = 0, cbReplyBytes = 0, cbWritten = 0; 
    char* pchReply   = (TCHAR*)HeapAlloc(hHeap, 0, 65536);

    fSuccess = ReadFile( 
         hDataPipe,        // handle to pipe 
         pchReply,    // buffer to receive data 
         65536, // size of buffer 
         &cbBytesRead, // number of bytes read 
         NULL);        // not overlapped I/O 
	LOG_FILE("getEtmData read %d\n",cbBytesRead );
	update_coverage_map(pchReply, cbBytesRead);
	HeapFree(hHeap,0,pchReply);
	return NULL;
}




BOOL writeData(HANDLE pipe, TCHAR* data, int size)
{
	BOOL fSuccess = FALSE;
	char cmdbuf[4] = {0};
	HANDLE hHeap      = GetProcessHeap();
	DWORD cbBytesRead = 0, cbReplyBytes = 0, cbWritten = 0; 
    //TCHAR* pchReply   = (TCHAR*)HeapAlloc(hHeap, 0, 65536*sizeof(TCHAR));
    fSuccess = WriteFile( 
         pipe,        // handle to pipe 
         data,    // buffer to receive data 
         size, // size of buffer 
         &cbWritten, // number of bytes read 
         NULL);        // not overlapped I/O 

	return fSuccess;
}



int run_target_t32(char **argv, uint32_t timeout) {
	int status;
	int ret = 0;
	char *cmd = argv_to_cmd(argv);
	TCHAR* pchReply;
	if (!child_handle) {
		t32_init(argv);
		LOG_FILE("Debug: run_target_t32 cmd :%s\n",cmd);
	
		setup_t32_main(cmd);
		

		fuzz_iterations_current = 0;
	}
	
	//send_cmd(CMD_INIT);

	status = waitfor_status(STATUS_READY);
	if (status != STATUS_READY)
	{
		LOG_FILE("wait error,%x\n",status);
	}
	send_cmd(CMD_GO);
	UINT32 i = 0;
	for (i = strlen(cmd); i > 0; i--)
	{
		if (cmd[i] == ' ')
		{
			break;
		}
		
	}
	

	writeData(hCtrlPipe,cmd+i+2, strlen(cmd)-i-2 );
	
	status = waitfor_status(STATUS_LOOP1DONE);
	if (status != STATUS_LOOP1DONE)
	{
		LOG_FILE("waitfor_status error:%x\n",status)
	}else{
		int count = get_etm_count();
		if(count > 0 && count <= 16384){
			pchReply = getEtmData();
			dbg_timeout_time = 0;
		}	
		else if( count == 0){

			if( dbg_timeout_time == 0)
				dbg_timeout_time = get_cur_time() + TRACE_TIMEOUT_MSEC;

			if (dbg_timeout_time > 0 && get_cur_time() > dbg_timeout_time)
			{
				LOG_FILE("Target may hanged for %d mSeconds\n",TRACE_TIMEOUT_MSEC)
				ret = FAULT_TMOUT; 
				dbg_timeout_time = 0;
			}
			
		}else
			LOG_FILE("get_etm_count error:%x\n",count)
	}
	ck_free(cmd);



	return ret;
}