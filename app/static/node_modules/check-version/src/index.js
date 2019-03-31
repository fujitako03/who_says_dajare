/**
 * @file check-version
 * @author xiaowu
 * @email fe.xiaowu@gmail.com
 */

'use strict';

import request from 'request';
import KeyCache from 'key-cache';

import config from '../config.json';

let cache = new KeyCache({
    dir: './cache/',
    md5key: false
});

export default () => {
    let promiseAll = [];

    let lastVertion = cache.get('lastVertion') || {};

    config.rule.forEach((val) => {
        let temp = new Promise((resolve, reject) => {
            request.get({
                headers: config.header,
                url: val.url
            }, (error, response, body) => {
                if (error) {
                    val.errcode = 1;
                    val.errmsg = error;
                    reject(val);
                }
                else if (response.statusCode !== 200) {
                    val.errcode = 2;
                    val.errmsg = response.statusCode;
                    reject(val);
                }
                else {
                    let reg = new RegExp(val.reg);
                    let match = val.match || '$1';
                    match = Math.floor(match.replace('$', '')) || 0;

                    try {
                        body = body.match(reg);
                        if (body && body.length > match - 1) {
                            body = body[match];
                        }

                    }
                    catch (e) {
                        body = null;
                    }

                    val.version = body;

                    resolve(val);
                }
            });
        });

        promiseAll.push(temp);
    });

    return Promise.all(promiseAll).then(data => {
        let res = {
            update: [],
            all: data
        };

        data.forEach(val => {
            let key = val.name;

            // 如果没有获取到版本
            if (!val.version) {
                return;
            }

            // 如果上个版本缓存过
            if (lastVertion.hasOwnProperty(key)) {
                if (val.version > lastVertion[key] || lastVertion[key] === null) {
                    val.lastVertion = lastVertion[key];
                    res.update.push(val);
                    lastVertion[key] = val.version;
                }
            }
            else {
                lastVertion[key] = val.version;
            }
        });

        cache.set('lastVertion', lastVertion);

        return res;
    });
};
