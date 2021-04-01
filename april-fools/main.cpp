#include <SDL2/SDL.h>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <stack>
#include <unistd.h>
#include <algorithm>

#define FRAMES 4382
#define WIDTH 28
#define HEIGHT 36

struct rect {
    int x, y, w, h;
};
    
std::vector<SDL_Window *> screens;

int frame[WIDTH][HEIGHT] = {};

struct rect * traverseRect(int i, int j)
{
    struct rect * result = (struct rect *) malloc(sizeof(struct rect *));
    int x = i+1, y = j+1;
    result->x = i;
    result->y = j;
    frame[i][j] = 2;
    bool xquit = false;
    bool yquit = false;
    while ((!xquit || !yquit) && x > i && y > j) {
        if (y < HEIGHT && !yquit) {
            for (int t=i; t<x; t++)
                if (!frame[t][y]) {
                    yquit = true; y--;
                    break;
                }
        }
        if (x < WIDTH && !xquit) {
            for (int t=j; t<y; t++)
                if (!frame[x][t]) {
                    xquit = true; x--;
                    break;
                }
        }
        if (y < HEIGHT && !yquit)
            for (int t=i; t<x; t++)
                frame[t][y] = 2;
        if (x < WIDTH && !xquit)
            for (int t=j; t<y; t++)
                frame[x][t] = 2;
        if (y < HEIGHT && x < WIDTH && !xquit && !yquit)
            frame[x][y] = 2;
        if (!xquit) x++; 
        if (!yquit) y++;
        if (x >= WIDTH) xquit = true;
        if (y >= HEIGHT) yquit = true;
        // std::cout << x << ' ' << y << '\n';
    }
    result->w = std::min(WIDTH, x-i);
    result->h = std::min(HEIGHT, y-j);
    return result;
}

struct rect * maxRect()
{
    for (int i=0; i<WIDTH; i++) {
        for (int j=0; j<HEIGHT; j++) {
            if (frame[i][j] == 1) {
                // std::cout << "Traversing from " << i << ", " << j << '\n';
                struct rect * result = traverseRect(i, j);
                return result;
            }
        }
    }
    return NULL;
}

SDL_Window * checkScreenExists(struct rect * result)
{
    for (SDL_Window * screen : screens) {
        int x, y, w, h;
        SDL_GetWindowPosition(screen, &y, &x);
        SDL_GetWindowSize(screen, &h, &w);
        y *= HEIGHT;
        y /= 1920;
        x *= WIDTH;
        x /= 1080;
        h *= HEIGHT;
        h /= 1920;
        w *= WIDTH;
        w /= 1080;
        if (std::abs(y - result->y) <= 1 && std::abs(x - result->x) <= 1 && std::abs(h - result->h) <= 1 && std::abs(w - result->w) <= 1)
            return screen;
    }
    return NULL;
}

void renderFrame()
{
    // for (int i=0; i<screens.size(); i++) {
    //     SDL_Window * screen = screens.at(i);
    //     if (!checkScreenOverlap(screen)) {
    //         SDL_DestroyWindow(screen);
    //         screens.erase(screens.begin()+i);
    //         i--;
    //     }
    // }
    // std::cout << "Overlap check successful\n";

    std::vector<SDL_Window *> newscreens;

    struct rect * result = maxRect();
    // std::cout << "Max rect check successful\n";
    while (result != NULL) {
        if (result->h > 0 && result->w > 0) {
            SDL_Window * screen = checkScreenExists(result);
            if (checkScreenExists(result) == NULL) {
                newscreens.push_back(SDL_CreateWindow("New Window", 
                    result->y * 1920/HEIGHT, result->x * 1080/WIDTH, result->h * 1920/HEIGHT, result->w * 1080/WIDTH, 0));
            } else {
                newscreens.push_back(screen);
                screens.erase(std::find(screens.begin(), screens.end(), screen));
            }
        }
        result = maxRect();
    }

    for (SDL_Window * screen : screens)
        SDL_DestroyWindow(screen);

    screens.clear();
    for (SDL_Window * screen : newscreens)
        screens.push_back(screen);
}

int main(int argc, char ** argv)
{
 
    SDL_Init(SDL_INIT_VIDEO);

    sleep(10);
    
    for (int t=0; t<FRAMES; t++) {

        std::cout << "Frame:" << t << '\n';
        
        for (int i=0; i<WIDTH; i++)
            for (int j=0; j<HEIGHT; j++) {
                scanf("%1d", &frame[i][j]);
                // std::cout << i << ' ' << j << '\n';
            }

        // for (int i=0; i<WIDTH; i++) {
        //     for (int j=0; j<HEIGHT; j++) {
        //         printf("%d", frame[i][j]);
        //         // std::cout << i << ' ' << j << '\n';
        //     }
        //     printf("\n");
        // }
        // printf("\n");

        // std::cout << "Input successful\n";

        renderFrame();

        // for (int i=0; i<WIDTH; i++) {
        //     for (int j=0; j<HEIGHT; j++) {
        //         printf("%d", frame[i][j]);
        //         // std::cout << i << ' ' << j << '\n';
        //     }
        //     printf("\n");
        // }
        // printf("\n");
 
        SDL_Delay(5);

    }

    for (SDL_Window * screen : screens)
        SDL_DestroyWindow(screen);
 
    SDL_Quit();
 
    return 0;
}