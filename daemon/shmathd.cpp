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

#define DAEMON_NAME "shmathd"

#define BUFSIZE 4096

static const char *fifoname = "/tmp/shmathp";
static char buffer[BUFSIZE+1];

void process(char *buffer) {
    syslog (LOG_NOTICE, buffer);
}   

int context_shmath(int fd) {
    int count;
    while((count = read(fd, buffer, BUFSIZE)) > 0) {
        process(buffer);    //Run our Process
        if (!strncmp(buffer, "exit", 4)) return -1;
    }
    return 0;
}

void context_mainloop() {
    int alive = 1;
    while(alive) {
        int fd = open(fifoname, O_RDONLY);
        if(fd < 0) {
            syslog(LOG_INFO, "Daemon failed to open /tmp/shmath");
            alive = 0;
        } else {
            syslog(LOG_INFO, "Daemon opened /tmp/shmath");
            if (context_shmath(fd)) alive = 0;
            close(fd);
        }
    }
    unlink(fifoname);
}

void context_fifoname() {
    errno = 0;
    if (mkfifo(fifoname, 0666) < 0) {
        syslog(LOG_INFO, "Daemon failed to create fifo");
    } else {
        context_mainloop();
    }
}

void context_umask() {
    mode_t umask_new = 0666;
    mode_t umask_old = umask(umask_new);
    context_fifoname();
    umask(umask_old);
}

void context_daemon() {

    /**** Begin initializing the daemon portion of the code ****/

    //Set our Logging Mask and open the Log
    setlogmask(LOG_UPTO(LOG_NOTICE));
    openlog(DAEMON_NAME, LOG_CONS | LOG_NDELAY | LOG_PERROR | LOG_PID, LOG_USER);

    syslog(LOG_INFO, "Entering Daemon");

    pid_t pid, sid;

   //Fork the Parent Process
    pid = fork();

    if (pid < 0) { exit(EXIT_FAILURE); }

    //We got a good pid, Close the Parent Process
    if (pid > 0) { exit(EXIT_SUCCESS); }

    //Change File Mask
    umask(0);

    //Create a new Signature Id for our child
    sid = setsid();
    if (sid < 0) { exit(EXIT_FAILURE); }

    //Change Directory
    //If we cant find the directory we exit with failure.
    if ((chdir("/")) < 0) { exit(EXIT_FAILURE); }

    //Close Standard File Descriptors
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);

    /**** End initializing the daemon portion of the code ****/

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
