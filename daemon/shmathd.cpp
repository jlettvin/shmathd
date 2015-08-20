/*
 * http://shahmirj.com/blog/beginners-guide-to-creating-a-daemon-in-linux
 */

#include <sys/types.h>
#include <sys/stat.h>
#include <syslog.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <fcntl.h>

// #define NDEBUG
// #include <libjson/libjson.h>

using namespace std;

#define PIPE_NAME "/tmp/shmathp"
#define DAEMON_NAME "shmathd"

#define BUFSIZE 4096

#define PASS_PIPE_MKFIFO   "[PASS] shmathd: mkfifo(/tmp/shmathp)"
#define FAIL_PIPE_MKFIFO   "[FAIL] shmathd: mkfifo(/tmp/shmathp)"
#define PASS_PIPE_OPEN     "[PASS] shmathd: open(/tmp/shmathp)"
#define FAIL_PIPE_OPEN     "[FAIL] shmathd: open(/tmp/shmathp)"
#define PASS_PIPE_CLOSE    "[PASS] shmathd: close(/tmp/shmathp)"
#define FAIL_PIPE_CLOSE    "[FAIL] shmathd: close(/tmp/shmathp)"
#define PASS_PIPE_UNLINK   "[PASS] shmathd: unlink(/tmp/shmathp)"
#define FAIL_PIPE_UNLINK   "[FAIL] shmathd: unlink(/tmp/shmathp)"
#define PASS_EXIT_SHMATHD  "[PASS] shmathd: exit"

static char buffer[BUFSIZE+1];
static int fd_named_pipe;
static int alive = 1;

void process(const char *buffer) {
    syslog (LOG_NOTICE, buffer);
}   

int context_shmath() {
    int count;
    while((count = read(fd_named_pipe, buffer, BUFSIZE)) > 0) {
        process(buffer);    //Run our Process
        if (!strncmp(buffer, "exit", 4)) {
            syslog(LOG_INFO, PASS_EXIT_SHMATHD);
            return -1;
        }
    }
    return 0;
}

void context_mainloop() {
    while(alive) {
        fd_named_pipe = open(PIPE_NAME, O_RDONLY);
        syslog(LOG_INFO,
                fd_named_pipe < 0 ? FAIL_PIPE_OPEN : PASS_PIPE_OPEN);
        if(fd_named_pipe < 0) {
            alive = 0;
        } else {
            if (context_shmath()) alive = 0;
            syslog(LOG_INFO,
                close(fd_named_pipe) ? FAIL_PIPE_CLOSE : PASS_PIPE_CLOSE);
        }
    }
    syslog(LOG_INFO,
            unlink(PIPE_NAME) ? FAIL_PIPE_UNLINK : PASS_PIPE_UNLINK);
}

void context_fifoname() {
    errno = 0;
    syslog(LOG_INFO,
            mkfifo(PIPE_NAME, 0666) < 0 ? FAIL_PIPE_MKFIFO : PASS_PIPE_MKFIFO);
    if (!errno) {
        context_mainloop();
    }
}

void context_umask() {
    mode_t umask_old = umask(0666);
    context_fifoname();
    umask(umask_old);
}

void context_daemon() { /**** Begin initializing daemon ****/
    //Set our Logging Mask and open the Log
    setlogmask(LOG_UPTO(LOG_NOTICE));
    openlog(DAEMON_NAME, LOG_CONS | LOG_NDELAY | LOG_PERROR | LOG_PID, LOG_USER);
    syslog(LOG_INFO, "Entering Daemon");

    //Fork the Parent Process
    //We got a good pid, Close the Parent Process
    pid_t pid, sid;
    pid = fork();
    if (pid < 0) { exit(EXIT_FAILURE); }
    if (pid > 0) { exit(EXIT_SUCCESS); }

    //Change File Mask
    umask(0);

    //Create a new Signature Id for our child
    sid = setsid();
    if (sid < 0) { exit(EXIT_FAILURE); }

    //Change directory, or If we cant find the directory we exit with failure.
    if ((chdir("/")) < 0) { exit(EXIT_FAILURE); }

    //Close Standard File Descriptors
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);

    /**** End initializing the daemon portion of the code and use daemon ****/
    context_umask();

    //Close the log
    syslog(LOG_INFO, "Exiting Daemon");
    closelog ();
}

int main(int argc, char *argv[]) {
    argc = argc;
    argv = argv;

    context_daemon();

    return 0;
}
