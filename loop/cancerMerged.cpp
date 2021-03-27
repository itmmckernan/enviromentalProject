#include <Python.h>
#include <vector>
using namespace std;
static struct PyModuleDef cancerMerged = {
    PyModuleDef_HEAD_INIT,
    "cancerMerged",   /* name of module */
};

static PyObject* calc(PyObject* self, PyObject* args){
    PyObject *argCounties=NULL, *argPowerPlants=NULL, *Out=NULL; //i am so very lost rn
    PyObject *countiesArray=NULL, *powerPlantsArray=NULL, *outputArr=NULL;
    //this parses the args?    idk what OOO is tho
    if(!PyArg_ParseTuple(args, "OOO!", &argCounties, &argPowerPlants, &PyArray_Type, &out))
        return NULL;

    //make the pyargs into actual arrays?
    arr1 = PyArray_FROM_OTF(argCounties, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
    if (arr1 == NULL)
        return NULL;
    arr2 = PyArray_FROM_OTF(argPowerPlants, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
    if (arr2 == NULL)
       goto fail;
}
static double toRadians(const double degree){
    return 0.0174532925199432957692369076848861271344287188854172545609719144*degree;
}

static double calcBackend(const vector<double> &mainCoord, const vector<vector<double>> &powerPlantPoints)
{
    double plantScore = 0;
    double radMainCoordLat = toRadians(mainCoord[0]);
    double radMainCoordLon = toRadians(mainCoord[1]);
    for(int i = 0; i < powerPlantPoints.size(); i++){
        double powerPlantLat = toRadians(powerPlantPoints[i][0]);
        double dLat = powerPlantLat - radMainCoordLat;
        double dLon = toRadians(powerPlantPoints[i][1]) - radMainCoordLon;
        plantScore += asin(sqrt(
                          pow(sin(dLat / 2), 2) +
                          cos(radMainCoordLat) * cos(powerPlantLat) *
                          pow(sin(dLon / 2), 2))) * 3956;
    }
    return plantScore
}


static PyMethodDef calcMethods[] = {
    {"calc", calc, METH_VARARGS,
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