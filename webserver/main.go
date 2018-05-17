package main

import (
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path"
	"strings"
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
	http.HandleFunc("/dic", dicHandler)
	http.Handle("/", http.FileServer(http.Dir(www)))
	panic(http.ListenAndServe(":"+*port, nil))
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

func dicHandler(w http.ResponseWriter, r *http.Request) {
	snap_common_dir := os.Getenv("SNAP_COMMON")

	configPath := path.Join(snap_common_dir, "dict.dic")

	config := []byte(r.FormValue("dic"))

	err := ioutil.WriteFile(configPath, config, 0644)
	check(err)

	w.WriteHeader(http.StatusOK)
}

func saveHandler(w http.ResponseWriter, r *http.Request) {
	snap_common_dir := os.Getenv("SNAP_COMMON")
	snap_user_common_dir := os.Getenv("SNAP_USER_COMMON")

	configPath := path.Join(snap_common_dir, "sphinx.cfg")

	config := []byte(strings.Replace(strings.Replace(r.FormValue("config"), "$SNAP_COMMON", snap_common_dir, -1), "$SNAP_USER_COMMON", snap_user_common_dir, -1))

	err := ioutil.WriteFile(configPath, config, 0644)
	check(err)

	w.WriteHeader(http.StatusOK)
}

func loadHandler(w http.ResponseWriter, r *http.Request) {
	snap_dir := os.Getenv("SNAP")
	snap_common_dir := os.Getenv("SNAP_COMMON")
	snap_user_common_dir := os.Getenv("SNAP_USER_COMMON")

	configPath := path.Join(snap_common_dir, "sphinx.cfg")

	config, err := ioutil.ReadFile(configPath)
	if err != nil {
		configPath = path.Join(snap_dir, "defaults/sphinx.cfg")
		config, err = ioutil.ReadFile(configPath)
		check(err)
	}
	check(err)

	s := string(config)
	w.Header().Set("Content-Type", "text/plain; charset=utf-8") // normal header
	w.WriteHeader(http.StatusOK)
	io.WriteString(w, strings.Replace(strings.Replace(strings.Replace(s,
		snap_common_dir, "$SNAP_COMMON", -1),
		snap_user_common_dir, "$SNAP_USER_COMMON", -1),
		snap_dir, "$SNAP", -1))
}

func setAuthHandler(w http.ResponseWriter, r *http.Request) {
	snap_common_dir := os.Getenv("SNAP_COMMON")

	configPath := path.Join(snap_common_dir, "token.cfg")

	config := []byte(r.FormValue("token") + "\n" + r.FormValue("name"))

	err := ioutil.WriteFile(configPath, config, 0644)
	check(err)

	w.WriteHeader(http.StatusOK)
}

func authHandler(w http.ResponseWriter, r *http.Request) {
	snap_dir := os.Getenv("SNAP")
	snap_common_dir := os.Getenv("SNAP_COMMON")

	configPath := path.Join(snap_common_dir, "token.cfg")

	config, err := ioutil.ReadFile(configPath)
	if err != nil {
		configPath = path.Join(snap_dir, "defaults/token.cfg")
		config, err = ioutil.ReadFile(configPath)
		check(err)
	}
	check(err)

	s := string(config)
	w.Header().Set("Content-Type", "text/plain; charset=utf-8") // normal header
	w.WriteHeader(http.StatusOK)
	io.WriteString(w, strings.Split(s, "\n")[1])
}
