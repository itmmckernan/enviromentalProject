#include <Python.h>


static struct PyModuleDef cancerMerged = {
    PyModuleDef_HEAD_INIT,
    "cancerMerged",   /* name of module */
};

static PyObject* calc(PyObject* self, PyObject* args){
    //do stuff in here?
    Py_RETURN_NONE;
}

static PyMethodDef calcMethods[] = {
    {"print_list", calc, METH_VARARGS,
     "A function that prints a list of strings."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef calcmodule = {
    PyModuleDef_HEAD_INIT,
    "Calc",   /* name of module */
    "calculates the function since python is slow af", /* module documentation */
    -1,
    calcMethods
};




PyMODINIT_FUNC
PyInit_cancerMerged(void) {
    PyObject* m = PyModule_Create(&cancerMerged);
    if (m == NULL) {
        return NULL;
    }
    return m;
}