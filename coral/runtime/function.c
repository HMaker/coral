#include <stdarg.h>
#include "runtime.h"


CRObjectArray* CRObjectArray_new(size_t maxLength) {
    CRObject** objects = NULL;
    if (maxLength > 0) {
        objects = (CRObject**) calloc(maxLength, sizeof(CRObject*));
        if (objects == NULL) {
            CR_ABORT("FATAL: CRObjectArray_new: failed to allocate new array container\n");
            return NULL;
        }
    }
    CRObjectArray* array = (CRObjectArray*) calloc(1, sizeof(CRObjectArray));
    if (array == NULL) {
        CR_ABORT("FATAL: CRObjectArray_new: failed to allocate new array\n");
        return NULL;
    }
    array->objects = objects;
    array->maxLength = maxLength;
    array->length = 0;
    return array;
}


void CRObjectArray_release(CRObjectArray* self) {
    CR_NOT_NULL(self);
    for (size_t i = 0; i < self->length; i++) {
        CRObject_decref(self->objects[i]);
    }
    CRObjectArray_destroy(self);
}


void CRObjectArray_destroy(CRObjectArray* self) {
    if (self == NULL) return;
    if (self->objects != NULL) {
        free(self->objects);
        self->objects = NULL;
    }
    free(self);
}


void CRObjectArray_push(CRObjectArray* self, CRObject* object) {
    CR_NOT_NULL(self);
    CR_NOT_NULL(object);
    if (self->length >= self->maxLength) {
        CR_ABORT("FATAL: CRObjectArray_push: tried to push to a full array\n");
        return;
    }
    self->objects[self->length] = object;
    self->length++;
}


void CRObjectArray_insert(CRObjectArray* self, size_t index, CRObject* object) {
    CR_NOT_NULL(self);
    CR_NOT_NULL(object);
    if (index >= self->maxLength) {
        CR_ABORT("FATAL: CRObjectArray_insert: index out of bounds\n");
        return;
    }
    self->objects[index] = object;
}


CRObject* CRObjectArray_get(CRObjectArray* self, size_t index) {
    CR_NOT_NULL(self);
    if (index >= self->maxLength) {
        CR_ABORT("FATAL: CRObjectArray_get: index out of bounds\n");
        return NULL;
    }
    return self->objects[index];
}


CRObject* CRFunction_new(
    size_t globalsSize,
    unsigned short arity,
    CRObject* (*fp) (CRObject**, CRObject**)
) {
    if (fp == NULL) {
        CR_ABORT("FATAL: CRFunction_new: received NULL function pointer\n");
        return NULL;
    }
    CRObject* obj = CRObject_new();
    CRFunction* func = (CRFunction*) calloc(1, sizeof(CRFunction));
    if (func == NULL) {
        CR_ABORT("FATAL: CRFunction_new: failed to allocate new function\n");
        return NULL;
    }
    func->globals = CRObjectArray_new(globalsSize);
    func->arity = arity;
    func->fp = fp;
    obj->_type = CR_FUNCTION;
    obj->value = func;
    return obj;
}


void CRFunction_destroy(CRFunction* self) {
    if (self == NULL) return;
    if (self->globals != NULL) {
        CRObjectArray_release(self->globals);
        self->globals = NULL;
    }
    self->fp = NULL;
    free(self);
}


void CRFunction_setGlobal(CRObject* self, size_t index, CRObject* global) {
    if (CRObject_getType(self) != CR_FUNCTION) {
        CR_ABORT("FATAL: CRFunction_setGlobal: called on non function\n");
        return;
    }
    CRFunction* func = (CRFunction*)self->value;
    CRObjectArray_insert(func->globals, index, global);
    CRObject_incref(global);
}


CRObject* CRFunction_call(CRObject* self, size_t argscount, ...) {
    CRType selftype = CRObject_getType(self);
    if (selftype != CR_FUNCTION) {
        CR_ABORT("FATAL: CRFunction_call: %s is not a callable\n", CRObject_getTypeName(self));
        return NULL;
    }
    CRFunction* func = (CRFunction*)self->value;
    if (argscount != func->arity) {
        CR_ABORT("FATAL: CRFunction_call: function expects %d arguments, but got %zu\n", func->arity, argscount);
        return NULL;
    }
    CRObject* result = NULL;
    if (argscount > 0) {
        va_list args;
        va_start(args, argscount);
        CRObjectArray* params = CRObjectArray_new(argscount);
        for (size_t i = 0; i < argscount; i++) {
            CRObjectArray_push(params, va_arg(args, CRObject*));
        }
        result = func->fp(func->globals->objects, params->objects);
        va_end(args);
        CRObjectArray_destroy(params);
    } else {
        result = func->fp(func->globals->objects, NULL);
    }
    if (result == NULL) {
        CR_ABORT("FATAL: CRFunction_call: function returned NULL\n");
        return NULL;
    }
    // the callee must clean the arguments, we just clean self
    CRObject_decref(self);
    return result;
}
