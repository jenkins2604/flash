#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/mman.h>

#define BSC_CR 0xF8048054
#define Disable_BUREG 0x66830000
#define FATAL do { fprintf(stderr, "Error at line %d, file %s (%d) [%s]\n", \
  __LINE__, __FILE__, errno, strerror(errno)); exit(1); } while(0)

static inline void *fixup_addr(void *addr, size_t size);

int main(int argc, char **argv) {
    int fd;
    void *map_base, *virt_addr; 
    uint32_t read_result;
    off_t target;
    uint32_t MAP_SIZE = sysconf(_SC_PAGE_SIZE);
    uint32_t MAP_MASK = (MAP_SIZE - 1);
    size_t data_size;
    
    target = BSC_CR;
    if((fd = open("/dev/mem", O_RDWR | O_SYNC)) == -1) FATAL;
    printf("/devmem start\n");
    map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);
    if(map_base == (void *) -1) FATAL;
    printf("Memory mapped at address %p.\n", map_base); 
    
    virt_addr = map_base + (target & MAP_MASK);
    data_size = sizeof(uint32_t);
    read_result = *((uint32_t *) virt_addr);
    
    printf("Original value of BSC_CR 0x%X\n", read_result); 
    
    *((uint32_t *) virt_addr) = Disable_BUREG;
    read_result = *((uint32_t *) virt_addr);
    if (Disable_BUREG == read_result) {
        printf("Succeed disable BSC_CR register in SAMA5D2\n. \
        Reboot device to enable binary mode and start flashing\n");
        }
    else {
        printf("Operation failed\n");
    }
    if(munmap(map_base, MAP_SIZE) == -1) {
        FATAL;
    }
    close(fd);
    return 0;
}
