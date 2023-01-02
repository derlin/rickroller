# How the RickRolling works

<!-- TOC start -->
- [Rick-rolling an URL](#rick-rolling-an-url)
- [How to absolutize URLs (links, images, resources)](#how-to-absolutize-urls-links-images-resources)
- [How to rickroll on user input](#how-to-rickroll-on-user-input)
- [Which link to redirect to?](#which-link-to-redirect-to)
<!-- TOC end -->

## Rick-rolling an URL

When this app receives an URL, it:
1. fetches the content using HTTP GET,
2. checks that there are no unsafe redirects to a private IP,
3. absolutizes the URLs found in the HTML,
4. adds some Javascript to trigger a redirection,
5. returns the modified HTML content to be served to the user.

The interesting points are 3 and 4.

## How to absolutize URLs (links, images, resources)

It is common in an HTML page to use *relative URLs* to refer to resources
found on the same server.
This is problematic when rick-rolling: since the page is served by the
rickroll service, relative links will fail. So how can we make those relative
URLs absolute?

One solution is to parse the file, find the relative URLs and use `urllib.urljoin`
to absolutize them relative to the base URL. Finding all the relative links is however
a big challenge as they can appear in many elements (`<img>`, `<script>`, `<link>`, etc).
They can also be used in different attributes, for example, `href` and `srcset` for images.
Even more problematic, they can appear in linked resources: how could we modify relative
URLs used in a CSS file (e.g. as `background-image`)?

Parsing the file is thus tedious, and will always have loopholes. Fortunately, there is
another way. Instead of changing the URLs themselves, we can change the base URL used
by the browser to resolve all relative URLs!

In HTML, this is done using the `<base>` tag:

> The `<base>` HTML element specifies the base URL to use for all *relative* URLs in a document.
> There can be only one `<base>` element in a document.
> [[src]](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base)

Thus, rickroller simply adds (or modifies) this `<base>` element in the header of the document.

## How to rickroll on user input

**Roll on click**

Suppose we want to redirect on click. The first instinct is to change all the `href` attributes
of `<a>` tags to point to the rickroll URL. This, however, is tedious and may tip off the user:
hovering over a link shows the URL on desktop. Even worse, some links are used for navigation or
other purposes than just redirecting, so the page may break unexpectedly.

A better, cleaner solution is to capture `click` events in Javascript and trigger the redirect
in the callback. This is perfect as long as we ensure our handler is triggered first and stops
event propagation.

Rickroller thus adds a `script` at the end of the body (last registered event wins):

```javascript
document.addEventListener("DOMContentLoaded", function(event) {
    document.addEventListener("click", e => {
        e.stopPropagation();
        e.preventDefault();
        window.location = "<RICKROLL URL>";
    }, true);
});
```

**Roll on scroll**

As people often do not interact with a page, but just read the content, redirecting on scroll
may improve the chances of rick-rolling.

There is no globally supported `scrollend` event (it exists, but no one implements it).
The closer we can get to detecting the end of scroll is:

```javascript
function scrollStop(callback, refresh = 250) {
    let isScrolling;
    window.addEventListener('scroll', function (event) {
        window.clearTimeout(isScrolling);
        isScrolling = setTimeout(callback, refresh);
    }, false);
}
```

In short, when the scroll begins, we run a function every X milliseconds and check if the
scroll still happens. If not, we have a `scrollend` event.
This works, but has some drawbacks: it will fire even if the user has still his two fingers
on the trackpad, as it only detects if the page stopped scrolling. I don't like it,
but I couldn't find a better way...

To avoid the rick-roll to happen too fast, this app let the user choose how many `scrollend`
events need to happen before the redirection.

(Note: someone proposed to register an event listener on `mouseup` when the scroll starts
instead of using a *timeout*, but this doesn't work with the mouse wheel, the trackpad,
or on mobile, so I haven't considered it further).

## Which link to redirect to?

**Autoplay with sounds**

Here is a good post about the difficulties of rick-rolling: [How to make a rickroll website](
https://dev.to/satvik/how-to-make-a-rickroll-website-28en):

> Chrome's autoplay policies are simple but this generally holds true for all browsers:
>
> 1. Muted autoplay is always allowed.
> 2. Autoplay with sound is allowed if:
> 3. **The user has interacted with the domain (click, tap, etc.).**
> 4. On desktop, the user's Media Engagement Index threshold has been crossed, meaning the user has previously played video with sound.
> 5. The user has added the site to their home screen on mobile or installed the PWA on desktop.
> 6. Top frames can delegate autoplay permission to their iframes to allow autoplay with sound. This make it really difficult to catch people offguard and rickrolling them as soon as they open up our website

Thus, starting a video automatically and with sounds on seems quite difficult without triggering voluntarily a user interaction
(e.g. by showing an "accept cookies" popup). The thing is, if we do that on RickRoller, it will be too obvious as the popup needs
to match the domain we are showing.

As a consequence, it is not possible to show an autoplay video with sound. Muting it, however, will make the autoplay work.

**Hosting Platform**

I first wanted to use YouTube, but:

1. most YouTube videos will start with ads,
2. without embed the link will open the app on mobile (which is slow and annoying),
3. Rick Roll videos have copyrighted content that makes the autoplay fail on mobile,
4. YouTube embeds do not work without a domain, meaning it is not possible to test a local site using IP addresses,
5. if YouTube has never been opened before, it will ask for some permissions, etc.

To avoid ads, it is possible to use [`yout-ube`](https://www.yout-ube.com) instead of `youtube`,
but the same embed limitations apply.

Instead of YouTube, I tried [streamable.com](https://streamable.com/e/shil2?autoplay=1) with an embed.
It doesn't have ads, but I wasn't able to get the autoplay working on mobile (even with sounds off).

I thought of hosting the video myself, but depending on the server the stream will be shaky and slow.

In the end, the best solution I found was to use a [giphy](https://giphy.com/clips/rick-roll-rolled-rolling-2KZ2v2vifTGTvGg1fu)
embed. Contrary to all other solutions, the autoplay works seamlessly, and the video is very fast to load -
way faster than any other solution!

(Note: I thought about showing an iframe with mute, then clicking on the unmute from JavaScript. This doesn't work due
to iframe's security features: "*Blocked a frame with origin "http://localhost:8080" from accessing a cross-origin frame.*").


