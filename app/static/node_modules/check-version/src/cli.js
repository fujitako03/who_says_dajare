/**
 * @file check-version
 * @author xiaowu
 * @email fe.xiaowu@gmail.com
 */

'use strict';

import Check from './index';

new Check().then(data => {
    console.log(data);
}).catch(err => {
    console.error(data);
});
