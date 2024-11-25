FROM itisfoundation/qooxdoo-kit:latest as build

WORKDIR /project

ENV PATH=/home/node/node_modules/.bin:$PATH

#COPY myapp .
RUN qx create myapp -t desktop -I

# copy code here and compile it
RUN cd myapp && \
    qx compile -t build


#####################################################
FROM python:3.7.12-alpine as production

WORKDIR /work
COPY --from=build /project/myapp/compiled/build/ .

EXPOSE 8000

ENTRYPOINT []
CMD python3 -m http.server 8000 --bind 0.0.0.0


# docker run -it -p 8080:8000 test
# serves in curl 127.0.0.1:8080/  | grep "myapp/boot.js" is non-zero
