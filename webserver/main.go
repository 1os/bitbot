package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
    "io/ioutil"
    "bufio"
	"os"
	"path"
)

func main() {
	port := flag.String("p", "8080", "port on which to serve web interfaces")
	flag.Usage = usage
	flag.Parse()

	if len(flag.Args()) != 1 {
		flag.Usage()
		log.Fatalf("Directory to serve relative to the snap root directory is the only required argument")
	}

	snapdir := os.Getenv("SNAP")
	www := path.Join(snapdir, flag.Arg(0))

    http.HandleFunc("/save", saveHandler)
    http.HandleFunc("/load", loadHandler)
    http.HandleFunc("/setAuth", setAuthHandler)
    http.HandleFunc("/auth", authHandler)
	panic(http.ListenAndServe(":"+*port, http.FileServer(http.Dir(www))))
}

func usage() {
	fmt.Fprintf(os.Stderr, "Usage of %s: [-p port] dir_to_serve\n", os.Args[0])
	flag.PrintDefaults()
}

func check(e error) {
    if e != nil {
        panic(e)
    }
}

func saveHandler(w http.ResponseWriter, r *http.Request) {
	snap_common_dir := os.Getenv("SNAP_COMMON")
	snap_user_common_dir := os.Getenv("SNAP_USER_COMMON")

	configPath := path.Join(snap_common_dir, "sphinx.cfg")

	config := []byte(Replace(Replace(r.FormValue("config"),"$SNAP_COMMON",snap_common_dir,-1),"$SNAP_USER_COMMON",snap_user_common_dir,-1))
	
    err := ioutil.WriteFile(configPath, config, 0644)
	check(err)
	
	w.WriteHeader(http.StatusOK)
}

func loadHandler(w http.ResponseWriter, r *http.Request) {
	snap_common_dir := os.Getenv("SNAP_COMMON")
	snap_user_common_dir := os.Getenv("SNAP_USER_COMMON")

	configPath := path.Join(snap_common_dir, "sphinx.cfg")

	config, err := ioutil.ReadFile(configPath)
    check(err)
	
	w.Header().Set("Content-Type", "text/plain; charset=utf-8") // normal header
	w.WriteHeader(http.StatusOK)
	io.WriteString(w, Replace(Replace(config,snap_common_dir,"$SNAP_COMMON",-1),snap_user_common_dir,"$SNAP_USER_COMMON",-1))
}

func setAuthHandler(w http.ResponseWriter, r *http.Request) {
	snap_common_dir := os.Getenv("SNAP_COMMON")

	configPath := path.Join(snap_common_dir, "token.cfg")

	config := []byte(r.FormValue("token"))
	
    err := ioutil.WriteFile(configPath, config, 0644)
	check(err)
	
	w.WriteHeader(http.StatusOK)
}

func authHandler(w http.ResponseWriter, r *http.Request) {
	snap_common_dir := os.Getenv("SNAP_COMMON")

	configPath := path.Join(snap_common_dir, "token.cfg")

	config, err := ioutil.ReadFile(configPath)
    check(err)
	
	w.Header().Set("Content-Type", "text/plain; charset=utf-8") // normal header
	w.WriteHeader(http.StatusOK)
	io.WriteString(w, config)
}