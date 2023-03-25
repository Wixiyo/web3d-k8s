#version 330 core
varying vec4 vCol;

void main() {
  // use vertex color
  gl_FragColor = vCol;
}